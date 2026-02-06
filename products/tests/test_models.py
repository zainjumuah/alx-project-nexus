from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from products.models import Category, Product


class CategoryModelTests(TestCase):
    def test_category_slug_unique_db_constraint(self):
        Category.objects.create(name="Phones", slug="phones")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Other Phones", slug="phones")

    def test_category_slug_unique_validation(self):
        Category.objects.create(name="Phones", slug="phones")
        dup = Category(name="Other Phones", slug="phones")

        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_category_name_unique_db_constraint(self):
        Category.objects.create(name="Laptops", slug="laptops")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Laptops", slug="laptops-2")

    def test_category_name_unique_validation(self):
        Category.objects.create(name="Laptops", slug="laptops")
        dup = Category(name="Laptops", slug="laptops-2")

        with self.assertRaises(ValidationError):
            dup.full_clean()


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Phones", slug="phones")

    def test_product_category_relationship(self):
        p = Product.objects.create(
            category=self.category,
            title="iPhone 16 Pro Max",
            description="Test",
            price=Decimal("1999.99"),
            stock=10,
            location="Lagos",
        )
        self.assertEqual(p.category, self.category)
        self.assertEqual(self.category.products.count(), 1)

    def test_product_price_cannot_be_negative_validation(self):
        p = Product(
            category=self.category,
            title="Bad Price",
            description="Test",
            price=Decimal("-1.00"),
            stock=1,
            location="Lagos",
        )

        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_product_price_cannot_be_negative_db_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    category=self.category,
                    title="Bad Price",
                    description="Test",
                    price=Decimal("-1.00"),
                    stock=1,
                    location="Lagos",
                )

    def test_product_stock_cannot_be_negative_validation(self):
        p = Product(
            category=self.category,
            title="Bad Stock",
            description="Test",
            price=Decimal("1.00"),
            stock=-5,
            location="Lagos",
        )

        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_product_stock_cannot_be_negative_db_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    category=self.category,
                    title="Bad Stock",
                    description="Test",
                    price=Decimal("1.00"),
                    stock=-5,
                    location="Lagos",
                )    
