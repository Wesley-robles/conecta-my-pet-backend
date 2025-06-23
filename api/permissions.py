# api/permissions.py
from rest_framework import permissions
from .models import PetShop

class IsPetShopOwner(permissions.BasePermission): # <-- NOME MUDOU
    """
    Permissão customizada para permitir que apenas o proprietário de um pet shop
    possa ver ou editar os objetos relacionados a ele.
    """
    def has_permission(self, request, view):
        petshop_pk = view.kwargs.get('petshop_pk')
        if not petshop_pk:
            return False

        try:
            petshop = PetShop.objects.get(pk=petshop_pk)
        except PetShop.DoesNotExist:
            return False

        # A regra agora verifica o campo 'owner'
        return petshop.owner == request.user # <-- LÓGICA MUDOU