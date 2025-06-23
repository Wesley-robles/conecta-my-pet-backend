from rest_framework import viewsets
# Adicione Service e ServiceSerializer às importações
from .models import PetShop, Service
from .serializers import PetShopSerializer, ServiceSerializer
from .permissions import IsPetShopOwner

class PetShopViewSet(viewsets.ModelViewSet):
    """
    Este ViewSet fornece automaticamente as ações `list`, `retrieve`,
    `create`, `update` e `destroy` para o modelo PetShop.
    """
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer

# VIEWSET PARA SERVIÇOS
class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsPetShopOwner]

    # Sobrescrevemos este método para retornar apenas
    # os serviços do pet shop especificado na URL.
    def get_queryset(self):
        # Acessamos o ID do pet shop que vem da URL
        petshop_pk = self.kwargs['petshop_pk']
        # Filtramos os serviços para retornar apenas os daquele pet shop
        return Service.objects.filter(pet_shop_id=petshop_pk)