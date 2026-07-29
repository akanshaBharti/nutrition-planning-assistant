from django.urls import path

from .views import NutritionItemListView

urlpatterns = [
    path('', NutritionItemListView.as_view(), name='nutrition-items'),
]
