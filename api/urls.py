# api/urls.py
from django.urls import path, include
# Importar os routers da nova biblioteca aninhada
from rest_framework_nested import routers
# Importar nossos ViewSets
from .views import PetShopViewSet, ServiceViewSet

# O router "pai" continua a existir para os petshops
router = routers.DefaultRouter()
router.register(r'petshops', PetShopViewSet, basename='petshop')

# Abaixo, criamos um router "filho" para aninhar os serviços
# O primeiro argumento é o router pai (router)
# O segundo é o prefixo do recurso pai na URL (r'petshops')
# O terceiro é o nome que usaremos para buscar o objeto pai (lookup='petshop')
petshops_router = routers.NestedDefaultRouter(router, r'petshops', lookup='petshop')

# Agora registramos o ViewSet de serviços NESTE router aninhado
petshops_router.register(r'services', ServiceViewSet, basename='petshop-services')

# Nossas urlpatterns agora incluem as URLs geradas por AMBOS os routers
urlpatterns = [
    path('', include(router.urls)),
    path('', include(petshops_router.urls)),
]