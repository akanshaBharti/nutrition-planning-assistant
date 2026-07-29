from django.db import models

from nutrition.models import NutritionItem


class Meal(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('other', 'Other'),
    ]

    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='other')
    original_text = models.TextField()
    total_calories = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    assumptions = models.JSONField(default=list, blank=True)
    uncertainty = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} {self.meal_type}: {self.total_calories} kcal"


class MealItem(models.Model):
    meal = models.ForeignKey(Meal, related_name='items', on_delete=models.CASCADE)
    nutrition_item = models.ForeignKey(
        NutritionItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    food_name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=40, blank=True)
    preparation_method = models.CharField(max_length=80, blank=True)
    estimated_calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    user_calories = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    assumptions = models.JSONField(default=list, blank=True)
    uncertainty = models.TextField(blank=True)
    source = models.CharField(max_length=240, blank=True)

    @property
    def final_calories(self):
        return self.user_calories if self.user_calories is not None else self.estimated_calories

    def __str__(self):
        return f"{self.food_name}: {self.final_calories} kcal"


class UserCorrection(models.Model):
    meal_item = models.ForeignKey(MealItem, related_name='corrections', on_delete=models.CASCADE)
    original_calories = models.DecimalField(max_digits=8, decimal_places=2)
    corrected_calories = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# Create your models here.
