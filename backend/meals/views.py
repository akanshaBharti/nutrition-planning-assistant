from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Meal
from .models import UserCorrection
from .serializers import MealSerializer, UserCorrectionSerializer
from .services import extract_meal


class MealExtractView(APIView):
    def post(self, request):
        description = (request.data.get('description') or '').strip()
        if not description:
            return Response({'description': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        result = extract_meal(description)
        if request.data.get('date'):
            result['date'] = request.data['date']
        if request.data.get('meal_type'):
            result['meal_type'] = request.data['meal_type']
        return Response(result)


class MealSaveView(APIView):
    def post(self, request):
        serializer = MealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        meal = serializer.save()
        return Response(MealSerializer(meal).data, status=status.HTTP_201_CREATED)


class DailyMealView(APIView):
    def get(self, request):
        selected_date = parse_date(request.query_params.get('date', ''))
        if selected_date is None:
            from datetime import date
            selected_date = date.today()
        meals = Meal.objects.filter(date=selected_date).prefetch_related('items')
        total = sum(meal.total_calories for meal in meals)
        return Response({
            'date': selected_date.isoformat(),
            'total_calories': total,
            'meals': MealSerializer(meals, many=True).data,
        })


class MealHistoryView(APIView):
    def get(self, request):
        meals = Meal.objects.prefetch_related('items')[:50]
        corrections = UserCorrection.objects.select_related('meal_item', 'meal_item__meal').order_by('-created_at')[:50]
        return Response({
            'meals': MealSerializer(meals, many=True).data,
            'corrections': UserCorrectionSerializer(corrections, many=True).data,
        })
