from rest_framework.test import APITestCase

from nutrition.models import NutritionItem
from profiles.models import UserProfile


class MealPlanWorkflowTests(APITestCase):
    def setUp(self):
        NutritionItem.objects.create(
            name='boiled egg',
            aliases=['egg'],
            dietary_tags=['vegetarian', 'high-protein'],
            preparation_method='boiled',
            serving_quantity=1,
            serving_unit='egg',
            calories=78,
            protein_g=6,
            carbs_g=0.6,
            fat_g=5.3,
            source='Test KB',
        )
        NutritionItem.objects.create(
            name='grilled chicken breast',
            aliases=['chicken'],
            dietary_tags=['high-protein'],
            preparation_method='grilled',
            serving_quantity=100,
            serving_unit='g',
            calories=165,
            protein_g=31,
            carbs_g=0,
            fat_g=3.6,
            source='Test KB',
        )
        NutritionItem.objects.create(
            name='banana',
            aliases=['banana'],
            dietary_tags=['vegetarian', 'vegan'],
            preparation_method='raw',
            serving_quantity=1,
            serving_unit='piece',
            calories=105,
            protein_g=1.3,
            carbs_g=27,
            fat_g=0.4,
            source='Test KB',
        )

    def test_generated_plan_applies_saved_restrictions_and_requires_approval(self):
        profile = UserProfile.current()
        profile.calorie_target = 1600
        profile.dietary_preferences = ['vegetarian']
        profile.allergies = ['chicken']
        profile.foods_to_avoid = ['banana']
        profile.save()

        generate_response = self.client.post('/api/plans/generate/', {}, format='json')
        self.assertEqual(generate_response.status_code, 201)

        plan = generate_response.json()
        self.assertEqual(plan['status'], 'draft')
        self.assertTrue(plan['items'])
        food_names = ' '.join(item['food_name'].lower() for item in plan['items'])
        self.assertNotIn('chicken', food_names)
        self.assertNotIn('banana', food_names)
        self.assertIn('Preference applied: vegetarian', plan['restrictions_applied'])

        approve_response = self.client.post(f"/api/plans/{plan['id']}/approve/", {}, format='json')

        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(approve_response.json()['status'], 'approved')
