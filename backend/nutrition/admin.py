from django.contrib import admin

from .models import NutritionItem


@admin.register(NutritionItem)
class NutritionItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'preparation_method', 'serving_quantity', 'serving_unit', 'calories')
    search_fields = ('name', 'preparation_method')

# Register your models here.
