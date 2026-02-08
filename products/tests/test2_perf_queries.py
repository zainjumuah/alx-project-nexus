from decimal import Decimal

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category, Product


def _rf_with_forced_pagination():
    rf = getattr(settings, "REST_FRAMEWORK", {}).copy()
    rf.update({
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 1000,  # big enough to return everything I create
    })
    return rf


@override_settings(REST_FRAMEWORK=_rf_with_forced_pagination())
class ProductQueryPerfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.cat = Category.objects.create(name="Phones", slug="phones")

    def _seed_products(self, n: int, offset: int = 0):
        for i in range(offset, offset + n):
            Product.objects.create(
                title=f"P{i}",
                description="x",
                price=Decimal("10.00") + i,
                stock=1,
                location="Lagos",
                category=self.cat,
            )

    def test_list_query_count_constant_even_when_products_increase(self):
        url = reverse("product-list")  # router default naming pattern
        self._seed_products(5)

        # With forced pagination: expected 2 queries:
        # 1) COUNT(*) for pagination
        # 2) SELECT ... JOIN category via select_related
        with self.assertNumQueries(2):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

        self._seed_products(200, offset=1000)

        # If select_related is removed, this becomes 2 + N (N+1) because serializer touches category fields.
        with self.assertNumQueries(2):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)

    def test_filter_and_ordering_do_not_increase_query_count(self):
        # These params may be implemented now or later.... anyhoo, they must not cause query explosions.
        url = reverse("product-list")
        self._seed_products(50)

        with self.assertNumQueries(2):
            resp = self.client.get(url, {"category": self.cat.id, "ordering": "price"})
            self.assertEqual(resp.status_code, 200)