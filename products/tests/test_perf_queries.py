from decimal import Decimal

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category, Product


def forced_rf_settings():
    """
    Merge existing REST_FRAMEWORK settings with deterministic pagination.
    This avoids accidentally dropping required defaults.
    """
    rf = dict(getattr(settings, "REST_FRAMEWORK", {}) or {})
    rf["DEFAULT_PAGINATION_CLASS"] = "rest_framework.pagination.PageNumberPagination"
    rf["PAGE_SIZE"] = 1000
    return rf


@override_settings(REST_FRAMEWORK=forced_rf_settings())
class ProductQueryPerfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Phones", slug="phones")

    def setUp(self):
        # Fresh client per test to avoid state leakage (auth headers, cookies, etc)
        self.client = APIClient()

    def _seed_products(self, n: int, offset: int = 0):
        products = []
        for i in range(offset, offset + n):
            products.append(
                Product(
                    title=f"P{i}",
                    description="x",
                    price=Decimal("10.00") + i,
                    stock=1,
                    location="Lagos",
                    category=self.cat,
                )
            )
        Product.objects.bulk_create(products)

    def _list_url(self):
        return reverse("product-list")

    def test_list_query_count_constant_even_when_products_increase(self):
        url = self._list_url()
        self._seed_products(5)

        with self.assertNumQueries(2):
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # proof the serializer is dereferencing category fields.
        # If this fails, my test is not protecting against N+1 at all, sad.
        first = resp.data["results"][0]
        self.assertIn("category_name", first)
        self.assertIn("category_slug", first)

        self._seed_products(200, offset=1000)

        with self.assertNumQueries(2):
            resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_filter_and_ordering_do_not_increase_query_count(self):
        url = self._list_url()
        self._seed_products(50)

        # I kept this strict on purpose: this should stay count query + page fetch query.
        with self.assertNumQueries(2):
            resp = self.client.get(url, {"category": self.cat.id, "ordering": "price"})
        self.assertEqual(resp.status_code, 200)

    def test_category_param_non_int_returns_400(self):
        url = self._list_url()
        self._seed_products(5)

        # I expect this to fail at validation stage before touching the DB.
        with self.assertNumQueries(0):
            resp = self.client.get(url, {"category": "abc"})
        self.assertEqual(resp.status_code, 400)

    def test_category_param_negative_returns_400(self):
        url = self._list_url()
        self._seed_products(5)

        # Same idea as above: invalid params should short-circuit before query execution. Pew
        with self.assertNumQueries(0):
            resp = self.client.get(url, {"category": -1})
        self.assertEqual(resp.status_code, 400)
