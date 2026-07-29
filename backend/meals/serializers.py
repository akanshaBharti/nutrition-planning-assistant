from rest_framework import serializers

from .models import Meal, MealItem, UserCorrection


class UserCorrectionSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='meal_item.food_name', read_only=True)
    meal_date = serializers.DateField(source='meal_item.meal.date', read_only=True)
    meal_type = serializers.CharField(source='meal_item.meal.meal_type', read_only=True)

    class Meta:
        model = UserCorrection
        fields = [
            'id',
            'food_name',
            'meal_date',
            'meal_type',
            'original_calories',
            'corrected_calories',
            'note',
            'created_at',
        ]


class MealItemSerializer(serializers.ModelSerializer):
    final_calories = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = MealItem
        fields = [
            'id',
            'nutrition_item',
            'food_name',
            'quantity',
            'unit',
            'preparation_method',
            'estimated_calories',
            'user_calories',
            'final_calories',
            'protein_g',
            'carbs_g',
            'fat_g',
            'assumptions',
            'uncertainty',
            'source',
        ]


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True)

    class Meta:
        model = Meal
        fields = [
            'id',
            'date',
            'meal_type',
            'original_text',
            'total_calories',
            'assumptions',
            'uncertainty',
            'created_at',
            'items',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        meal = Meal.objects.create(**validated_data)
        total = 0
        for item_data in items_data:
            user_calories = item_data.get('user_calories')
            estimated = item_data.get('estimated_calories') or 0
            meal_item = MealItem.objects.create(meal=meal, **item_data)
            total += user_calories if user_calories is not None else estimated
            if user_calories is not None and user_calories != estimated:
                UserCorrection.objects.create(
                    meal_item=meal_item,
                    original_calories=estimated,
                    corrected_calories=user_calories,
                )
        meal.total_calories = total
        meal.save(update_fields=['total_calories'])
        return meal
