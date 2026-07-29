from django.urls import path

from .views import DailyMealView, MealExtractView, MealHistoryView, MealSaveView

urlpatterns = [
    path('extract/', MealExtractView.as_view(), name='meal-extract'),
    path('save/', MealSaveView.as_view(), name='meal-save'),
    path('daily/', DailyMealView.as_view(), name='daily-meals'),
    path('history/', MealHistoryView.as_view(), name='meal-history'),
]
