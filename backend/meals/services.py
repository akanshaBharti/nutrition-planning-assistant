import re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from nutrition.models import NutritionItem


QUANTITY_RE = re.compile(
    r'(?P<qty>\d+(?:\.\d+)?|half|one|two|three|four)\s*(?P<unit>cups?|g|grams?|pieces?|slices?|large egg|eggs?|tbsp|tablespoons?)?',
    re.IGNORECASE,
)

NUMBER_WORDS = {
    'half': Decimal('0.5'),
    'one': Decimal('1'),
    'two': Decimal('2'),
    'three': Decimal('3'),
    'four': Decimal('4'),
}

PREPARATION_WORDS = [
    'boiled',
    'grilled',
    'fried',
    'steamed',
    'cooked',
    'raw',
    'roasted',
    'baked',
]


def _decimal(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _round(value):
    return _decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _normalize_unit(unit):
    if not unit:
        return ''
    unit = unit.lower().strip()
    replacements = {
        'cups': 'cup',
        'grams': 'g',
        'gram': 'g',
        'pieces': 'piece',
        'eggs': 'egg',
        'tablespoons': 'tbsp',
    }
    return replacements.get(unit, unit)


def _quantity_from_text(text):
    match = QUANTITY_RE.search(text)
    if not match:
        return None, ''
    raw_qty = match.group('qty').lower()
    quantity = NUMBER_WORDS.get(raw_qty, Decimal(raw_qty))
    return quantity, _normalize_unit(match.group('unit') or '')


def _preparation_from_text(text):
    lowered = text.lower()
    for word in PREPARATION_WORDS:
        if word in lowered:
            return word
    return ''


def _all_names(item):
    return [item.name.lower(), *[alias.lower() for alias in item.aliases]]


def find_nutrition_item(fragment, preparation_method=''):
    matches = candidate_nutrition_items(fragment)
    if not matches:
        return None
    if preparation_method:
        exact_method = [
            item for item in matches
            if item.preparation_method.lower() == preparation_method.lower()
        ]
        if exact_method:
            return exact_method[0]
    without_method = [item for item in matches if not item.preparation_method]
    return without_method[0] if without_method else matches[0]


def candidate_nutrition_items(fragment):
    lowered = fragment.lower()
    items = list(NutritionItem.objects.all())
    return [item for item in items if any(name in lowered for name in _all_names(item))]


def _scaled_nutrition(item, quantity, unit):
    assumptions = []
    serving_quantity = _decimal(item.serving_quantity)
    ratio = Decimal('1')

    if quantity is None:
        assumptions.append(
            f"Used documented serving size: {item.serving_quantity} {item.serving_unit}."
        )
    elif _normalize_unit(unit) == _normalize_unit(item.serving_unit):
        ratio = quantity / serving_quantity
    elif not unit:
        assumptions.append(
            f"Quantity had no unit, treated as {quantity} x documented serving."
        )
        ratio = quantity
    else:
        assumptions.append(
            f"Unit '{unit}' differs from documented serving '{item.serving_unit}', treated as one documented serving."
        )

    return {
        'estimated_calories': _round(item.calories * ratio),
        'protein_g': _round(item.protein_g * ratio),
        'carbs_g': _round(item.carbs_g * ratio),
        'fat_g': _round(item.fat_g * ratio),
        'assumptions': assumptions,
    }


def _infer_unit(fragment, item, unit):
    if unit or item is None:
        return unit
    lowered = fragment.lower()
    serving_unit = _normalize_unit(item.serving_unit)
    possible_units = {serving_unit, f"{serving_unit}s"}
    if serving_unit == 'egg':
        possible_units.update({'egg', 'eggs'})
    if serving_unit == 'piece':
        possible_units.update({'piece', 'pieces'})
    if any(candidate and candidate in lowered for candidate in possible_units):
        return serving_unit
    return unit


def extract_meal(description):
    fragments = [part.strip() for part in re.split(r',|\band\b|\n', description) if part.strip()]
    items = []
    clarification_questions = []
    assumptions = []

    for fragment in fragments:
        quantity, unit = _quantity_from_text(fragment)
        preparation_method = _preparation_from_text(fragment)
        nutrition_item = find_nutrition_item(fragment, preparation_method)

        if not nutrition_item:
            items.append({
                'nutrition_item': None,
                'food_name': fragment,
                'quantity': quantity,
                'unit': unit,
                'preparation_method': preparation_method,
                'estimated_calories': Decimal('0'),
                'protein_g': Decimal('0'),
                'carbs_g': Decimal('0'),
                'fat_g': Decimal('0'),
                'assumptions': [],
                'uncertainty': 'No documented nutrition value was found. Please enter calories manually or choose a KB food.',
                'source': '',
            })
            clarification_questions.append(f"What documented food should '{fragment}' map to, or what calories should be used?")
            continue

        unit = _infer_unit(fragment, nutrition_item, unit)

        if quantity is None:
            clarification_questions.append(f"How much {nutrition_item.name} did you have?")

        method_options = NutritionItem.objects.filter(name__iexact=nutrition_item.name).exclude(preparation_method='')
        candidate_methods = {
            item.preparation_method
            for item in candidate_nutrition_items(fragment)
            if item.preparation_method
        }
        if method_options.count() > 1 and not preparation_method:
            methods = ', '.join(sorted({item.preparation_method for item in method_options}))
            clarification_questions.append(f"How was the {nutrition_item.name} prepared? Options in the knowledge base: {methods}.")
        elif len(candidate_methods) > 1 and not preparation_method:
            methods = ', '.join(sorted(candidate_methods))
            clarification_questions.append(f"How was '{fragment}' prepared? Options in the knowledge base: {methods}.")

        scaled = _scaled_nutrition(nutrition_item, quantity, unit)
        item_assumptions = scaled.pop('assumptions')
        assumptions.extend(item_assumptions)
        items.append({
            'nutrition_item': nutrition_item.id,
            'food_name': nutrition_item.name,
            'quantity': quantity or nutrition_item.serving_quantity,
            'unit': unit or nutrition_item.serving_unit,
            'preparation_method': preparation_method or nutrition_item.preparation_method,
            'source': nutrition_item.source,
            'uncertainty': 'Review needed.' if item_assumptions else '',
            **scaled,
            'assumptions': item_assumptions,
        })

    total = sum(_decimal(item['estimated_calories']) for item in items)
    return {
        'requires_clarification': bool(clarification_questions),
        'clarification_questions': clarification_questions[:2],
        'date': date.today().isoformat(),
        'meal_type': 'other',
        'original_text': description,
        'total_calories': _round(total),
        'assumptions': assumptions,
        'uncertainty': 'Some items need clarification or manual correction.' if clarification_questions else '',
        'items': items,
    }
