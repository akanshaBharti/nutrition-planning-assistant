from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from config.workflow_logging import workflow_log
from nutrition.models import NutritionItem
from profiles.models import UserProfile


MEAL_SPLIT = [
    ('breakfast', Decimal('0.25')),
    ('lunch', Decimal('0.35')),
    ('dinner', Decimal('0.30')),
    ('snack', Decimal('0.10')),
]


def _round(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _blocked_terms(profile):
    return [term.lower() for term in [*profile.allergies, *profile.foods_to_avoid] if term]


def _matches_preference(item, preferences):
    if not preferences:
        return True
    tags = {tag.lower() for tag in item.dietary_tags}
    normalized = {preference.lower() for preference in preferences}
    if 'vegetarian' in normalized and 'vegetarian' not in tags:
        return False
    if 'vegan' in normalized and 'vegan' not in tags:
        return False
    return True


def eligible_items(profile):
    blocked = _blocked_terms(profile)
    allowed = []
    for item in NutritionItem.objects.all():
        searchable = ' '.join([
            item.name,
            item.preparation_method,
            ' '.join(item.aliases),
            ' '.join(item.dietary_tags),
        ]).lower()
        if any(term in searchable for term in blocked):
            continue
        if not _matches_preference(item, profile.dietary_preferences):
            continue
        allowed.append(item)
    return allowed


def generate_plan():
    profile = UserProfile.current()
    target_date = timezone.localdate() + timedelta(days=1)
    foods = eligible_items(profile)
    workflow_log(
        'meal_plan_generation_started',
        calorie_target=profile.calorie_target,
        preference_count=len(profile.dietary_preferences),
        allergy_count=len(profile.allergies),
        foods_to_avoid_count=len(profile.foods_to_avoid),
        eligible_food_count=len(foods),
    )
    if not foods:
        result = {
            'target_date': target_date,
            'status': 'draft',
            'total_calories': Decimal('0'),
            'assumptions': ['No eligible foods were found in the nutrition knowledge base.'],
            'restrictions_applied': [
                *[f"Allergy avoided: {item}" for item in profile.allergies],
                *[f"Food avoided: {item}" for item in profile.foods_to_avoid],
                *[f"Preference applied: {item}" for item in profile.dietary_preferences],
            ],
            'items': [],
        }
        workflow_log('meal_plan_generation_completed', item_count=0, total_calories=result['total_calories'], status='draft')
        return result

    sorted_foods = sorted(foods, key=lambda item: abs(Decimal(item.calories) - Decimal('350')))
    items = []
    total = Decimal('0')
    for index, (meal_type, share) in enumerate(MEAL_SPLIT):
        item = sorted_foods[index % len(sorted_foods)]
        target_calories = Decimal(profile.calorie_target) * share
        quantity_multiplier = max(Decimal('0.5'), target_calories / Decimal(item.calories))
        quantity = _round(Decimal(item.serving_quantity) * quantity_multiplier)
        calories = _round(Decimal(item.calories) * quantity_multiplier)
        total += calories
        items.append({
            'nutrition_item': item.id,
            'meal_type': meal_type,
            'food_name': item.name,
            'quantity': quantity,
            'unit': item.serving_unit,
            'preparation_method': item.preparation_method,
            'calories': calories,
            'protein_g': _round(Decimal(item.protein_g) * quantity_multiplier),
            'carbs_g': _round(Decimal(item.carbs_g) * quantity_multiplier),
            'fat_g': _round(Decimal(item.fat_g) * quantity_multiplier),
            'rationale': 'Selected from documented nutrition items while applying saved preferences and restrictions.',
        })

    result = {
        'target_date': target_date,
        'status': 'draft',
        'total_calories': _round(total),
        'assumptions': [
            'Plan uses only foods available in the local nutrition knowledge base.',
            'Quantities are scaled from documented serving sizes to approach the saved calorie target.',
        ],
        'restrictions_applied': [
            *[f"Allergy avoided: {item}" for item in profile.allergies],
            *[f"Food avoided: {item}" for item in profile.foods_to_avoid],
            *[f"Preference applied: {item}" for item in profile.dietary_preferences],
        ],
        'items': items,
    }
    workflow_log(
        'meal_plan_generation_completed',
        item_count=len(items),
        total_calories=result['total_calories'],
        status='draft',
    )
    return result
