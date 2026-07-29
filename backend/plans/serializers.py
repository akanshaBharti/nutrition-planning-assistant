from rest_framework import serializers

from .models import MealPlan, MealPlanItem


class MealPlanItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlanItem
        fields = [
            'id',
            'nutrition_item',
            'meal_type',
            'food_name',
            'quantity',
            'unit',
            'preparation_method',
            'calories',
            'protein_g',
            'carbs_g',
            'fat_g',
            'rationale',
        ]


class MealPlanSerializer(serializers.ModelSerializer):
    items = MealPlanItemSerializer(many=True)

    class Meta:
        model = MealPlan
        fields = [
            'id',
            'target_date',
            'status',
            'total_calories',
            'assumptions',
            'restrictions_applied',
            'created_at',
            'updated_at',
            'items',
        ]

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if items_data is not None:
            instance.items.all().delete()
            total = 0
            for item_data in items_data:
                MealPlanItem.objects.create(plan=instance, **item_data)
                total += item_data.get('calories') or 0
            instance.total_calories = total
        instance.save()
        return instance
