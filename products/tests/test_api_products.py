from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework.test import APIClient

from products.models import Category, Product


class ProductsAPIPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Category required for product creation payloads
        cls.category = Category.objects.create(name="Phones", slug="phones")

        # Create a product for PATCH test (optional but strong)
        cls.product = Product.objects.create(
            category=cls.category,
            title="Seed Product",
            description="Seed",
            price=Decimal("100.00"),
            stock=5,
            location="Lagos",
        )

        # Create a user for auth tests (works with custom USERNAME_FIELD)
        User = get_user_model()
        username_field = User.USERNAME_FIELD

        identifier = "test@example.com" if username_field == "email" else "testuser"
        create_kwargs = {username_field: identifier}

        # If the model has an email field and it's not the login identifier, set it anyway
        if username_field != "email" and any(f.name == "email" for f in User._meta.fields):
            create_kwargs["email"] = "test@example.com"

        cls.password = "Pass1234!Strong"
        cls.user = User.objects.create_user(**create_kwargs, password=cls.password)
        cls.login_identifier = identifier
        cls.username_field = username_field

    def setUp(self):
        self.client = APIClient()

    # ---------- Helpers ----------

    def _products_list_url(self):
        return reverse("product-list")

    def _products_detail_url(self, pk):
        return reverse("product-detail", args=[pk])

    def _token_url(self):
        try:
            return reverse("token_obtain_pair")
        except NoReverseMatch as e:
            raise AssertionError("JWT token endpoint name 'token_obtain_pair' is missing/broken in urls.py") from e

    def _resp_debug(self, resp):
        data = getattr(resp, "data", None)
        if data is not None:
            return f"data={data}"
        try:
            return f"content={resp.content.decode(errors='replace')}"
        except Exception:
            return f"raw_content={resp.content!r}"

    def _get_access_token(self):
        payload = {self.username_field: self.login_identifier, "password": self.password}
        resp = self.client.post(self._token_url(), payload, format="json")
        if resp.status_code in (200, 201) and isinstance(resp.data, dict):
            token = resp.data.get("access") or resp.data.get("token")
            if token:
                return token

        raise AssertionError(
            "Could not obtain JWT token.\n"
            f"Tried: {self._token_url()}\n"
            f"Last status: {resp.status_code}\n"
            f"Last response: {self._resp_debug(resp)}"
        )

    def _auth_client(self):
        token = self._get_access_token()
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return c

    def _valid_product_payload(self):
        return {
            "category": self.category.id,
            "title": "iPhone 16 Pro Max",
            "description": "Test product",
            "price": "1999.99",
            "stock": 10,
            "location": "Lagos",
        }

    # ---------- Tests (P0 requirements) ----------

    def test_products_list_allows_anonymous(self):
        resp = self.client.get(self._products_list_url())
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("application/json"))
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, resp.data)

    def test_products_create_rejects_anonymous(self):
        resp = self.client.post(self._products_list_url(), self._valid_product_payload(), format="json")
        self.assertIn(resp.status_code, (401, 403))  # choose one later if you want strictness

    def test_products_create_allows_authenticated(self):
        auth_client = self._auth_client()
        resp = auth_client.post(self._products_list_url(), self._valid_product_payload(), format="json")

        self.assertEqual(resp.status_code, 201)
        self.assertIn("id", resp.data)
        created_id = resp.data["id"]

        # Category can be returned as an int FK or a nested object depending on serializer
        cat_val = resp.data.get("category")
        if isinstance(cat_val, int):
            self.assertEqual(cat_val, self.category.id)
        elif isinstance(cat_val, dict):
            self.assertEqual(cat_val.get("id"), self.category.id)
        else:
            raise AssertionError(f"Unexpected category representation: {cat_val}")

        get_resp = self.client.get(self._products_detail_url(created_id))
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.data["id"], created_id)

    # Optional
    def test_products_update_rejects_anonymous(self):
        resp = self.client.patch(
            self._products_detail_url(self.product.id),
            {"title": "Hacked Title"},
            format="json",
        )
        self.assertIn(resp.status_code, (401, 403))

    def test_products_delete_rejects_anonymous(self):
        resp = self.client.delete(self._products_detail_url(self.product.id))
        self.assertIn(resp.status_code, (401, 403))
