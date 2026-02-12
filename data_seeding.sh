#!/bin/bash
python manage.py shell -c "
from decimal import Decimal
from products.models import Category, Product

c, _ = Category.objects.get_or_create(name='Stable Verify', slug='stable-verify')
Product.objects.filter(category=c).delete()

# 10 products with identical price (tie-case)
for i in range(1, 11):
    Product.objects.create(
        category=c,
        title=f'STABLE-EQ-{i:02d}',
        description='tie-price test',
        price=Decimal('100.00'),
        stock=1,
        location='Lagos',
    )

# 10 products with different prices
for i in range(1, 11):
    Product.objects.create(
        category=c,
        title=f'STABLE-UNIQ-{i:02d}',
        description='unique-price test',
        price=Decimal(str(100 + i)),
        stock=1,
        location='Lagos',
    )

print(c.id)
"
