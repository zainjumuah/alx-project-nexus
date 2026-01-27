from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModuleAdmin):
    list_display = ('title', 'price', 'stock', 'created_at')
    search_fields = ('title', 'description')
    list_ilter = ('category',)
