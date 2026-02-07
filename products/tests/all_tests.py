import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APIClient

from products.models import Category


class CategoryAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        suffix = uuid.uuid4().hex[:8]
        identifier = f"zaintheuser{suffix}@example.com" if username_field == "email" else f"zaintheuser{suffix}"
        create_kwargs = {username_field: identifier}

        if username_field != "email" and any(f.name == "email" for f in User._meta.fields):
            create_kwargs["email"] = f"catuser{suffix}@example.com"

        cls.password = "Pass1234!Strong"
        cls.user = User.objects.create_user(**create_kwargs, password=cls.password)
        cls.login_identifier = identifier
        cls.username_field = username_field

    def setUp(self):
        self.client = APIClient()

    def _unique_payload(self):
        suffix = uuid.uuid4().hex[:8]
        return {"name": f"Category {suffix}", "slug": f"category-{suffix}"}

    def _categories_list_url(self):
        return reverse("category-list")

    def _categories_detail_url(self, pk):
        return reverse("category-detail", args=[pk])

    def _token_url(self):
        try:
            return reverse("token_obtain_pair")
        except NoReverseMatch as e:
            raise AssertionError("JWT token endpoint name 'token_obtain_pair' is missing/broken in urls.py") from e

    def _resp_debug(self, res):
        data = getattr(res, "data", None)
        if data is not None:
            return f"data={data}"
        try:
            return f"content={res.content.decode(errors='replace')}"
        except Exception:
            return f"raw_content={res.content!r}"

    def _auth_client(self):
        token_payload = {self.username_field: self.login_identifier, "password": self.password}
        res = self.client.post(self._token_url(), token_payload, format="json")
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            msg=f"Token obtain failed: {res.status_code} {self._resp_debug(res)}",
        )
        token = res.data["access"]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_anonymous_list_categories_200(self):
        Category.objects.create(**self._unique_payload())
        res = self.client.get(self._categories_list_url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res["Content-Type"].startswith("application/json"))
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, res.data)

    def test_anonymous_detail_category_200(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.get(self._categories_detail_url(cat.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res["Content-Type"].startswith("application/json"))

    def test_anonymous_create_category_blocked(self):
        res = self.client.post(self._categories_list_url(), self._unique_payload(), format="json")
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_patch_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.patch(
            self._categories_detail_url(cat.id),
            {"name": "Blocked Update"},
            format="json",
        )
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_anonymous_delete_category_blocked(self):
        cat = Category.objects.create(**self._unique_payload())
        res = self.client.delete(self._categories_detail_url(cat.id))
        self.assertIn(res.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_auth_create_category_201_and_persists(self):
        auth_client = self._auth_client()
        payload = self._unique_payload()
        res = auth_client.post(self._categories_list_url(), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", res.data)
        self.assertEqual(res.data["name"], payload["name"])
        self.assertEqual(res.data["slug"], payload["slug"])

        created_id = res.data["id"]
        self.assertTrue(Category.objects.filter(id=created_id).exists())

        get_res = self.client.get(self._categories_detail_url(created_id))
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["name"], payload["name"])
        self.assertEqual(get_res.data["slug"], payload["slug"])

    def test_auth_patch_category_200_and_persists(self):
        cat = Category.objects.create(**self._unique_payload())
        auth_client = self._auth_client()

        new_name = f"{cat.name} Updated"
        res = auth_client.patch(
            self._categories_detail_url(cat.id),
            {"name": new_name},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        cat.refresh_from_db()
        self.assertEqual(cat.name, new_name)

    def test_auth_delete_204_and_get_after_delete_404(self):
        cat = Category.objects.create(**self._unique_payload())
        auth_client = self._auth_client()

        del_res = auth_client.delete(self._categories_detail_url(cat.id))
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        get_res = self.client.get(self._categories_detail_url(cat.id))
        self.assertEqual(get_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_create_duplicate_slug_fails(self):
        auth_client = self._auth_client()
        payload = {"name": "A", "slug": "dup-slug"}
        auth_client.post(self._categories_list_url(), payload, format="json")
        res = auth_client.post(
            self._categories_list_url(),
            {"name": "B", "slug": "dup-slug"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

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

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category, Product


class ProductDiscoveryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat1 = Category.objects.create(name="Phones", slug="phones")
        cls.cat2 = Category.objects.create(name="Laptops", slug="laptops")

        Product.objects.create(
            title="P3", description="d", price=Decimal("30.00"), stock=1, category=cls.cat1
        )
        Product.objects.create(
            title="P1", description="d", price=Decimal("10.00"), stock=1, category=cls.cat1
        )
        Product.objects.create(
            title="P2", description="d", price=Decimal("20.00"), stock=1, category=cls.cat1
        )
        Product.objects.create(
            title="L1", description="d", price=Decimal("5.00"), stock=1, category=cls.cat2
        )

    def setUp(self):
        self.client = APIClient()

    def _products_list_url(self):
        return reverse("product-list")

    def test_filter_order_paginated(self):
        url = self._products_list_url()
        resp = self.client.get(url, {"category": self.cat1.id, "ordering": "price", "page": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("application/json"))

        # paginated DRF format
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, resp.data)

        results = resp.data["results"]
        prices = [Decimal(str(item["price"])) for item in results]

        # category filter applied (supports either FK int or nested)
        for item in results:
            cat_val = item["category"]
            cat_id = cat_val if isinstance(cat_val, int) else cat_val.get("id")
            self.assertEqual(cat_id, self.cat1.id)

        self.assertEqual(prices, sorted(prices))

    def test_order_desc(self):
        url = self._products_list_url()
        resp = self.client.get(url, {"category": self.cat1.id, "ordering": "-price", "page": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp["Content-Type"].startswith("application/json"))
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, resp.data)

        results = resp.data["results"]
        prices = [Decimal(str(item["price"])) for item in results]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_bad_category_type_returns_400(self):
        url = self._products_list_url()
        resp = self.client.get(url, {"category": "abc"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("category", resp.data)

    def test_nonexistent_category_returns_empty(self):
        url = self._products_list_url()
        resp = self.client.get(url, {"category": 999999})
        self.assertEqual(resp.status_code, 200)
        for key in ("count", "next", "previous", "results"):
            self.assertIn(key, resp.data)
        self.assertEqual(resp.data["count"], 0)
        self.assertEqual(resp.data["results"], [])
