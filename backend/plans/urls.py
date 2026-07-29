from django.urls import path

from .views import (
    MealPlanApproveView,
    MealPlanDetailView,
    MealPlanGenerateView,
    MealPlanListView,
    MealPlanRejectView,
)

urlpatterns = [
    path('', MealPlanListView.as_view(), name='meal-plan-list'),
    path('generate/', MealPlanGenerateView.as_view(), name='meal-plan-generate'),
    path('<int:plan_id>/', MealPlanDetailView.as_view(), name='meal-plan-detail'),
    path('<int:plan_id>/approve/', MealPlanApproveView.as_view(), name='meal-plan-approve'),
    path('<int:plan_id>/reject/', MealPlanRejectView.as_view(), name='meal-plan-reject'),
]
