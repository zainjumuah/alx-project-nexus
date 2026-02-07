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
