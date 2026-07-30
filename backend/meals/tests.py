from datetime import date

from rest_framework.test import APITestCase

from nutrition.models import NutritionItem


class MealWorkflowTests(APITestCase):
    def setUp(self):
        NutritionItem.objects.create(
            name='grilled chicken breast',
            aliases=['chicken', 'chicken breast'],
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
            name='fried chicken breast',
            aliases=['fried chicken', 'chicken'],
            dietary_tags=['high-protein'],
            preparation_method='fried',
            serving_quantity=100,
            serving_unit='g',
            calories=260,
            protein_g=25,
            carbs_g=8,
            fat_g=14,
            source='Test KB',
        )
        NutritionItem.objects.create(
            name='cooked white rice',
            aliases=['rice'],
            dietary_tags=['vegetarian', 'vegan'],
            preparation_method='cooked',
            serving_quantity=1,
            serving_unit='cup',
            calories=205,
            protein_g=4.3,
            carbs_g=44.5,
            fat_g=0.4,
            source='Test KB',
        )

    def test_extracts_structured_items_and_clarifies_missing_details(self):
        response = self.client.post('/api/meals/extract/', {'description': 'chicken and rice'}, format='json')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['requires_clarification'])
        self.assertEqual(len(payload['items']), 2)
        self.assertIn('How much', payload['clarification_questions'][0])
        self.assertTrue(any('prepared' in question for question in payload['clarification_questions']))
        self.assertEqual(payload['items'][0]['source'], 'Test KB')
        self.assertGreater(float(payload['total_calories']), 0)

    def test_unknown_food_is_uncertain_instead_of_invented(self):
        response = self.client.post('/api/meals/extract/', {'description': 'mystery stew'}, format='json')

        self.assertEqual(response.status_code, 200)
        item = response.json()['items'][0]
        self.assertEqual(float(item['estimated_calories']), 0)
        self.assertIn('No documented nutrition value', item['uncertainty'])

    def test_saving_user_correction_preserves_history(self):
        payload = {
            'date': date.today().isoformat(),
            'meal_type': 'lunch',
            'original_text': '100g grilled chicken',
            'total_calories': '165.00',
            'assumptions': [],
            'uncertainty': '',
            'items': [
                {
                    'food_name': 'grilled chicken breast',
                    'quantity': '100.00',
                    'unit': 'g',
                    'preparation_method': 'grilled',
                    'estimated_calories': '165.00',
                    'user_calories': '180.00',
                    'protein_g': '31.00',
                    'carbs_g': '0.00',
                    'fat_g': '3.60',
                    'assumptions': [],
                    'uncertainty': '',
                    'source': 'Test KB',
                }
            ],
        }

        save_response = self.client.post('/api/meals/save/', payload, format='json')
        history_response = self.client.get('/api/meals/history/')

        self.assertEqual(save_response.status_code, 201)
        self.assertEqual(history_response.status_code, 200)
        history = history_response.json()
        self.assertEqual(len(history['meals']), 1)
        self.assertEqual(len(history['corrections']), 1)
        self.assertEqual(float(history['corrections'][0]['corrected_calories']), 180)
