from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category


class CategoriesAPIPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Phones", slug="phones")

        User = get_user_model()
        username_field = User.USERNAME_FIELD

        identifier = "test@example.com" if username_field == "email" else "testuser"
        create_kwargs = {username_field: identifier}

        if username_field != "email" and any(f.name == "email" for f in User._meta.fields):
            create_kwargs["email"] = "test@example.com"

        cls.password = "Pass1234!Strong"
        cls.user = User.objects.create_user(**create_kwargs, password=cls.password)
        cls.login_identifier = identifier
        cls.username_field = username_field

    def setUp(self):
        self.client = APIClient()

    # ---------- Helpers ----------

    def _categories_list_url(self):
        return reverse("category-list")

    def _categories_detail_url(self, pk):
        return reverse("category-detail", args=[pk])

    def _token_url(self):
        return reverse("token_obtain_pair")

    def _get_access_token(self):
        payload = {self.username_field: self.login_identifier, "password": self.password}
        resp = self.client.post(self._token_url(), payload, format="json")
        if resp.status_code in (200, 201) and isinstance(resp.data, dict):
            token = resp.data.get("access") or resp.data.get("token")
            if token:
                return token
        raise AssertionError(f"Token obtain failed: {resp.status_code} {getattr(resp, 'data', None)}")

    def _auth_client(self):
        token = self._get_access_token()
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return c

    def _valid_category_payload(self):
        # keep minimal to avoid schema mismatch
        return {"name": "Laptops", "slug": "laptops"}

    # ---------- Tests ----------

    def test_categories_list_allows_anonymous(self):
        resp = self.client.get(self._categories_list_url())
        self.assertEqual(resp.status_code, 200)

    def test_categories_create_rejects_anonymous(self):
        resp = self.client.post(self._categories_list_url(), self._valid_category_payload(), format="json")
        self.assertIn(resp.status_code, (401, 403))

    def test_categories_create_allows_authenticated(self):
        auth_client = self._auth_client()
        resp = auth_client.post(self._categories_list_url(), self._valid_category_payload(), format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)

    def test_categories_update_rejects_anonymous(self):
        resp = self.client.patch(
            self._categories_detail_url(self.category.id),
            {"name": "Hacked"},
            format="json",
        )
        self.assertIn(resp.status_code, (401, 403))

    def test_categories_delete_rejects_anonymous(self):
        resp = self.client.delete(self._categories_detail_url(self.category.id))
        self.assertIn(resp.status_code, (401, 403))
