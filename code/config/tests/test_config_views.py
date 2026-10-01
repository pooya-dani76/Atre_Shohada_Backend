import os
from unittest import mock

from django.test import RequestFactory, TestCase
from django.urls import reverse

from config.permissions import HasSwaggerAPIKey


API_KEY = "test-database-api-key"
ACCESS_DENIED_DETAIL = "Access denied: Invalid or missing API key."


class HasSwaggerAPIKeyTestCase(TestCase):
    """Tests for the API key permission that protects the schema & docs endpoints"""

    def setUp(self):
        self.permission = HasSwaggerAPIKey()

    def test_permission_is_granted_with_header_api_key(self):
        request = RequestFactory().get('/api/schema/', HTTP_X_API_KEY=API_KEY)
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            self.assertTrue(self.permission.has_permission(request, None))

    def test_permission_is_granted_with_query_param_api_key(self):
        request = RequestFactory().get('/api/schema/', {'api_key': API_KEY})
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            self.assertTrue(self.permission.has_permission(request, None))

    def test_permission_is_denied_without_api_key(self):
        request = RequestFactory().get('/api/schema/')
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            self.assertFalse(self.permission.has_permission(request, None))

    def test_permission_is_denied_with_invalid_api_key(self):
        request = RequestFactory().get('/api/schema/', HTTP_X_API_KEY="wrong-api-key")
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            self.assertFalse(self.permission.has_permission(request, None))


class SecureSchemaViewTestCase(TestCase):
    """Tests for the API key protected OpenAPI schema endpoint"""

    def setUp(self):
        self.url = reverse('schema')

    def test_schema_is_returned_with_valid_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url, {'api_key': API_KEY})
        self.assertEqual(response.status_code, 200)

    def test_schema_is_forbidden_without_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], ACCESS_DENIED_DETAIL)

    def test_schema_is_forbidden_with_invalid_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url, {'api_key': "wrong-api-key"})
        self.assertEqual(response.status_code, 403)


class SecureSwaggerViewTestCase(TestCase):
    """Tests for the API key protected swagger UI endpoint"""

    def setUp(self):
        self.url = reverse('swagger-ui')

    def test_swagger_ui_is_returned_with_valid_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url, {'api_key': API_KEY})
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui_is_forbidden_without_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], ACCESS_DENIED_DETAIL)

    def test_swagger_ui_is_forbidden_with_invalid_api_key(self):
        with mock.patch.dict(os.environ, {"DATABASE_API_KEY": API_KEY}):
            response = self.client.get(self.url, {'api_key': "wrong-api-key"})
        self.assertEqual(response.status_code, 403)
