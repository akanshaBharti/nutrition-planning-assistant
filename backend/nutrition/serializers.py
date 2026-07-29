from rest_framework import serializers

from .models import NutritionItem


class NutritionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionItem
        fields = [
            'id',
            'name',
            'aliases',
            'dietary_tags',
            'preparation_method',
            'serving_quantity',
            'serving_unit',
            'calories',
            'protein_g',
            'carbs_g',
            'fat_g',
            'source',
            'notes',
        ]
