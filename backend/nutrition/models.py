from django.db import models


class NutritionItem(models.Model):
    name = models.CharField(max_length=120)
    aliases = models.JSONField(default=list, blank=True)
    dietary_tags = models.JSONField(default=list, blank=True)
    preparation_method = models.CharField(max_length=80, blank=True)
    serving_quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    serving_unit = models.CharField(max_length=40)
    calories = models.DecimalField(max_digits=8, decimal_places=2)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    source = models.CharField(max_length=240)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'preparation_method']

    def __str__(self):
        method = f", {self.preparation_method}" if self.preparation_method else ""
        return f"{self.name}{method} ({self.serving_quantity} {self.serving_unit})"

# Create your models here.
