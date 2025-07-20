# api/permissions.py
from rest_framework import permissions
from .models import PetShop, Appointment

# Em api/permissions.py

class CanManagePetShop(permissions.BasePermission):
    """
    Permissão customizada que permite acesso apenas ao Proprietário
    ou a um Gerente daquele pet shop específico. (VERSÃO DE DEPURAÇÃO)
    """
    def has_permission(self, request, view):
        petshop_pk = view.kwargs.get('petshop_pk')
        if not petshop_pk:
            return False
        
        try:
            petshop = PetShop.objects.get(pk=petshop_pk)
        except PetShop.DoesNotExist:
            return False

        user = request.user
        
        # --- INÍCIO DO CÓDIGO DE DEPURAÇÃO ---
        print("--- Verificando Permissão para Gerenciar PetShop ---")
        print(f"Usuário: {user.username} (Tipo: {user.user_type})")
        print(f"Tentando aceder ao PetShop: {petshop.name} (ID: {petshop.id})")
        print(f"PetShop onde o usuário trabalha (works_at): {user.works_at}")
        # --- FIM DO CÓDIGO DE DEPURAÇÃO ---

        is_owner = petshop.owner == user
        is_manager = (user.user_type == 'GERENTE' and user.works_at == petshop)
        
        # --- INÍCIO DO CÓDIGO DE DEPURAÇÃO ---
        print(f"Verificação 'is_owner': {is_owner}")
        print(f"Verificação 'is_manager': {is_manager}")
        print("-------------------------------------------------")
        # --- FIM DO CÓDIGO DE DEPURAÇÃO ---
        
        return is_owner or is_manager

class IsAppointmentOwnerOrPetShopOwner(permissions.BasePermission):
    """
    Permite acesso a um Agendamento para o Tutor que o criou
    ou para a equipe do PetShop onde ele foi agendado.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        is_tutor_owner = (user.user_type == 'TUTOR' and obj.tutor == user)
        is_shop_owner = obj.pet_shop.owner == user
        is_shop_staff = user.user_type in ['GERENTE', 'FUNCIONARIO'] and user.works_at == obj.pet_shop

        return is_tutor_owner or is_shop_owner or is_shop_staff