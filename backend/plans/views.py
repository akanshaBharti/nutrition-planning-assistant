from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from config.workflow_logging import workflow_log
from .models import MealPlan, MealPlanItem
from .serializers import MealPlanSerializer
from .services import generate_plan


class MealPlanListView(ListAPIView):
    queryset = MealPlan.objects.prefetch_related('items')
    serializer_class = MealPlanSerializer


class MealPlanGenerateView(APIView):
    def post(self, request):
        plan_data = generate_plan()
        items_data = plan_data.pop('items')
        plan = MealPlan.objects.create(**plan_data)
        for item_data in items_data:
            nutrition_item_id = item_data.pop('nutrition_item', None)
            if nutrition_item_id:
                item_data['nutrition_item_id'] = nutrition_item_id
            MealPlanItem.objects.create(plan=plan, **item_data)
        return Response(MealPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class MealPlanDetailView(APIView):
    def patch(self, request, plan_id):
        plan = get_object_or_404(MealPlan, pk=plan_id)
        serializer = MealPlanSerializer(plan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MealPlanApproveView(APIView):
    def post(self, request, plan_id):
        plan = get_object_or_404(MealPlan, pk=plan_id)
        plan.status = MealPlan.STATUS_APPROVED
        plan.save(update_fields=['status', 'updated_at'])
        workflow_log('meal_plan_reviewed', plan_id=plan.id, action='approved', total_calories=plan.total_calories)
        return Response(MealPlanSerializer(plan).data)


class MealPlanRejectView(APIView):
    def post(self, request, plan_id):
        plan = get_object_or_404(MealPlan, pk=plan_id)
        plan.status = MealPlan.STATUS_REJECTED
        plan.save(update_fields=['status', 'updated_at'])
        workflow_log('meal_plan_reviewed', plan_id=plan.id, action='rejected', total_calories=plan.total_calories)
        return Response(MealPlanSerializer(plan).data)
