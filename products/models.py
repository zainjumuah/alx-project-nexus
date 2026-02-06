from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        #indexes = [models.Index(fields=["slug"]),] I'm editing you out because I have set slug unique=True

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )
    title = models.CharField(max_length=255) #
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, blank=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gte=0), 
                name="product_price_gte_0",
                ),
            models.CheckConstraint(
                condition=Q(stock__gte=0), 
                name="product_stock_gte_0",
                ), #uneeded, stock is defined with a PositiveIntegerField field type but I need it for db_level constraint tests
        ]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["category", "price"]),
        ]
    
    def __str__(self) -> str:
        return self.title