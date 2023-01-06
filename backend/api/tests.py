import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.conf import settings

from rest_framework.test import APIClient, APITestCase
from recipes.models import Recipe

User = get_user_model()

class UsersEndpointsTest(APITestCase):
    """
    Класс для тестирования эндпоинтов api. Эмулирует ручное тестирование.
    """
    @classmethod
    def setUpClass(cls):
        call_command('loaddata', '../data/data_dump_20230106.json', verbosity=0)
        cls.client = APIClient()
        cls.auth_client = APIClient()
        cls.user=User.objects.get(username='povar')
        cls.auth_client.force_authenticate(user=cls.user)

        cls.data = {
            'name': 'Картошка',
            'text': 'Свари картошку',
            'cooking_time': 20,
            'ingredients': [
                {
                    'id': 1,
                    'amount': 10
                }
            ],
            'tags': [
                1
            ]
        }

        cls.UPD_RECIPE = 2
        cls.UPD_STRANGER_RECIPE = 1
        cls.NOT_EXISTS_RECIPE = 99

        return super().setUpClass()

    def test_tags_list(self):
        response = self.client.get('/api/v1/tags/?page=2')
        tag = response.data['results'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tag['slug'], 'vypechka')

    def test_tags_retrieve(self):
        response = self.client.get('/api/v1/tags/1/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v1/tags/10/')
        self.assertEqual(response.status_code, 404)

    def test_recipe_list_retrieve(self):
        response = self.client.get('/api/v1/recipes/?author=5')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v1/recipes/?is_favorited=0')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v1/recipes/?is_in_shopping_cart=1')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v1/recipes/?tags=breakfast')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v1/recipes/1/')
        self.assertEqual(response.status_code, 200)

    def test_create_recipe_auth(self):
        """Проверяет аутентификацию при создании рецепта"""

        response = self.client.post(
            '/api/v1/recipes/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.post(
            '/api/v1/recipes/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 201)

    def test_update_recipe_auth(self):
        """Проверяет аутентиф. и авториз. при обновлении рецепта"""
        self.data['text'] = 'Свари картошку и пожарь ее'
        self.data['cooking_time'] = 30

        response = self.client.patch(
            f'/api/v1/recipes/{self.UPD_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.patch(
            f'/api/v1/recipes/{self.UPD_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['cooking_time'], 30)

        response = self.auth_client.patch(
            f'/api/v1/recipes/{self.UPD_STRANGER_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 403)

        response = self.auth_client.patch(
            f'/api/v1/recipes/{self.NOT_EXISTS_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 404)

    def test_update_recipe_data(self):
        """Проверяет реакцию на неправильные поля"""
        self.data['ingredients'] = [
            {
                'id': 1,
                'amount': -1
            }
        ]
        response = self.auth_client.patch(
            f'/api/v1/recipes/{self.UPD_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('amount', response.data.get('ingredients')[0].keys())


        self.data['ingredients'] = [
            {
                'id': 1,
                'amount': 0.5
            }
        ]
        response = self.auth_client.patch(
            f'/api/v1/recipes/{self.UPD_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('amount', response.data.get('ingredients')[0].keys())

    def test_delete_recipe(self):
        """Проверяет статусы при удалении рецептов"""
        response = self.client.delete(
            f'/api/v1/recipes/{self.UPD_STRANGER_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.delete(
            f'/api/v1/recipes/{self.UPD_STRANGER_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 403)

        response = self.auth_client.delete(
            f'/api/v1/recipes/{self.NOT_EXISTS_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 404)

        response = self.auth_client.delete(
            f'/api/v1/recipes/{self.UPD_RECIPE}/',
            data=self.data, format='json'
        )
        self.assertEqual(response.status_code, 204)