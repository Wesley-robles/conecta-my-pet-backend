# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PetShopViewSet

# 1. Cria um router
router = DefaultRouter()

# 2. Registra nosso ViewSet com o router, definindo o prefixo da URL como 'petshops'
router.register(r'petshops', PetShopViewSet, basename='petshop')

# 3. As URLs da API são agora determinadas automaticamente pelo router.
urlpatterns = [
    path('', include(router.urls)),
]