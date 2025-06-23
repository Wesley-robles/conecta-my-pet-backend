from rest_framework import viewsets
from .models import PetShop
from .serializers import PetShopSerializer

class PetShopViewSet(viewsets.ModelViewSet):
    """
    Este ViewSet fornece automaticamente as ações `list`, `retrieve`,
    `create`, `update` e `destroy` para o modelo PetShop.
    """
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer