from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category',)
    ordering = ("-created_at",)
