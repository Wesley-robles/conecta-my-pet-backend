# api/urls.py
from django.urls import path, include
from rest_framework_nested import routers
from .views import PetShopViewSet, ServiceViewSet, PetViewSet, AppointmentViewSet, TimeBlockViewSet

# 1. Router principal (pai)
router = routers.DefaultRouter()
router.register(r'petshops', PetShopViewSet, basename='petshop')
router.register(r'pets', PetViewSet, basename='pet')
router.register(r'agendamentos', AppointmentViewSet, basename='appointment')
router.register(r'bloqueios', TimeBlockViewSet, basename='timeblock')

# 2. Router aninhado (filho) para os serviços
petshops_router = routers.NestedDefaultRouter(router, r'petshops', lookup='petshop')
petshops_router.register(r'services', ServiceViewSet, basename='petshop-services')

# 3. Lista final de URLs, incluindo ambos os routers
urlpatterns = [
    path('', include(router.urls)),
    path('', include(petshops_router.urls)),
]