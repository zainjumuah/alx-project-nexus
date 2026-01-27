from django.db import models

# Create your models here.
class Product(models.Model):
    title = models.CharField(max_length=255) #
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    #will create image and categpory fields
    def __str__(self):
        return self.title