# api/permissions.py
from rest_framework import permissions
from .models import PetShop, Appointment # Appointment precisa estar importado

class IsPetShopOwner(permissions.BasePermission):
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

        return petshop.owner == request.user

# VERIFIQUE SE ESTA CLASSE EXISTE E ESTÁ CORRETA
class IsAppointmentOwnerOrPetShopOwner(permissions.BasePermission):
    """
    Permite acesso a um Agendamento apenas para o Tutor que o criou
    ou para o Proprietário do PetShop onde ele foi agendado.
    """
    def has_object_permission(self, request, view, obj):
        # 'obj' aqui é a instância do Agendamento que está sendo acessado.
        is_tutor_owner = obj.tutor == request.user
        is_petshop_owner = obj.pet_shop.owner == request.user
        
        # A permissão é concedida se QUALQUER uma das condições for verdadeira.
        return is_tutor_owner or is_petshop_owner