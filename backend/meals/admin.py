from django.contrib import admin

from .models import Meal, MealItem, UserCorrection


class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 0


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('date', 'meal_type', 'total_calories', 'created_at')
    inlines = [MealItemInline]


admin.site.register(UserCorrection)

# Register your models here.
