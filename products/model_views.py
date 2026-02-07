from rest_framework import viewsets, permissions
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly



class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]