from django.contrib.auth import get_user_model

from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class UsersEndpointsTest(APITestCase):
    """
    Класс для тестирования эндпоинтов users. Эмулирует ручное тестирование.
    """
    @classmethod
    def setUpClass(cls):
        for i in range(10):
            User.objects.create(
                username = f'user{i+1}',
                email = f'user{i+1}@mail.com',
            )
        cls.client = APIClient()
        cls.auth_client = APIClient()
        cls.user=User.objects.get(id=1)
        cls.auth_client.force_authenticate(user=cls.user)

        cls.flds = [
            'first_name',
            'last_name',
            'email',
            'username',
            'is_subscribed',
            'password'
        ]

        return super().setUpClass()

    def assertFields(self, response_fields, fields_in, fields_not_in=[]):
        """Проверка наличия и отсутствия полей в response."""
        for field in fields_in:
            if field in fields_not_in:
                continue
            with self.subTest(field=field):
                self.assertIn(field, response_fields.keys())
        for field in fields_not_in:
            with self.subTest(field=field):
                self.assertNotIn('password', response_fields.keys())

    def test_user_list_200_pagination_fields(self):
        """Проверка списка польз.: статус, пагинация, поля и отсутствия пароля."""
        response = self.client.get('/api/users/', {'limit': 2, 'offset': 2})
        user = response.data['results'][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user['username'], 'user3')
        self.assertFields(
            response.data['results'][0],
            self.flds,
            ['password']
        )

    def test_user_signup(self):
        """Проверка добавл. польз.: статус, поля и отсутствия пароля."""
        initial_data = {
            'first_name': 'first',
            'last_name': 'last',
        }
        additional_data = {
            'email': 'userx@mail.com',
            'username': 'userx',
            'password': 'serdit'
        }
        response = self.client.post('/api/users/', data=initial_data)
        self.assertEqual(response.status_code, 400)
        for field in additional_data.keys():
            with self.subTest(field=field):
                self.assertIn(field, response.data.keys())
        
        data={**initial_data, **additional_data}
        response = self.client.post('/api/users/', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertFields(response.data, self.flds, ['password', 'is_subscribed'])

    def test_user_profile(self):
        """Проверка get польз.: статус, авториз., поля и отсутствия пароля."""
        response = self.client.get('/api/users/1/')
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.get('/api/users/1/')
        self.assertEqual(response.status_code, 200)
        self.assertFields(response.data, self.flds, ['password'])

    def test_user_profile_me(self):
        """Проверка get польз.: статус, авториз., поля и отсутствия пароля."""
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertFields(response.data, self.flds, ['password'])

    def test_change_password(self):
        """Проверка смены пароля.: статус, авториз., поля."""
        response = self.client.post('/api/users/set_password/')
        self.assertEqual(response.status_code, 401)

        response = self.auth_client.post('/api/users/set_password/')
        self.assertEqual(response.status_code, 400)
        self.assertFields(response.data, ['new_password', 'current_password'])

    def test_create_token(self):
        """Проверка получ. токена: статус, поля."""
        data = {
            'first_name': 'first',
            'last_name': 'last',
            'email': 'userx@mail.com',
            'username': 'userx',
            'password': 'serdit',
        }
        response = self.client.post('/api/users/', data=data)
        response = self.client.post('/api/auth/token/login/')
        self.assertEqual(response.status_code, 400)

        response = self.client.post('/api/auth/token/login/', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFields(response.data, ['auth_token'])           


    def test_delete_token(self):
        """Проверка удал. токена: статус, поля."""
        response = self.auth_client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, 204)
        response = self.client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, 401)
