from rest_framework.generics import ListAPIView

from .models import NutritionItem
from .serializers import NutritionItemSerializer


class NutritionItemListView(ListAPIView):
    queryset = NutritionItem.objects.all()
    serializer_class = NutritionItemSerializer
