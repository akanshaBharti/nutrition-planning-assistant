from django.db import models

from nutrition.models import NutritionItem


class MealPlan(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    target_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    total_calories = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    assumptions = models.JSONField(default=list, blank=True)
    restrictions_applied = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-target_date', '-created_at']

    def __str__(self):
        return f"{self.target_date} plan ({self.status})"


class MealPlanItem(models.Model):
    plan = models.ForeignKey(MealPlan, related_name='items', on_delete=models.CASCADE)
    nutrition_item = models.ForeignKey(
        NutritionItem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    meal_type = models.CharField(max_length=20)
    food_name = models.CharField(max_length=120)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=40)
    preparation_method = models.CharField(max_length=80, blank=True)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    rationale = models.TextField(blank=True)

    class Meta:
        ordering = ['id']

# Create your models here.
