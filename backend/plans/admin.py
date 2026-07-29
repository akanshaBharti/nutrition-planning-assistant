from django.contrib import admin

from .models import MealPlan, MealPlanItem


class MealPlanItemInline(admin.TabularInline):
    model = MealPlanItem
    extra = 0


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('target_date', 'status', 'total_calories', 'created_at')
    inlines = [MealPlanItemInline]

# Register your models here.
