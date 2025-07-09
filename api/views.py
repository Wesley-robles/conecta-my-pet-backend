from rest_framework import viewsets, permissions, serializers
from rest_framework.permissions import IsAuthenticated

# Nossos Modelos
from .models import (
    User,
    PetShop,
    Service,
    Pet,
    Appointment
)

# Nossos Serializers
from .serializers import (
    PetShopSerializer,
    ServiceSerializer,
    PetSerializer,
    AppointmentSerializer
)

# Nossas Permissões Customizadas
from .permissions import IsPetShopOwner, IsAppointmentOwnerOrPetShopOwner


class PetShopViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar e editar Pet Shops.
    """
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer
    permission_classes = [IsAuthenticated] # Exige autenticação para tudo


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para os Serviços de um PetShop específico (rota aninhada).
    """
    serializer_class = ServiceSerializer
    permission_classes = [IsPetShopOwner] # Regra customizada: apenas o dono do petshop pode gerenciar

    def get_queryset(self):
        """
        Retorna apenas os serviços do pet shop especificado na URL.
        """
        petshop_pk = self.kwargs['petshop_pk']
        return Service.objects.filter(pet_shop_id=petshop_pk)


class PetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para um Tutor visualizar e gerenciar seus próprios Pets.
    """
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra o queryset para retornar apenas os pets do usuário logado.
        """
        return Pet.objects.filter(tutor=self.request.user)

    def perform_create(self, serializer):
        """
        Define o tutor do novo pet como sendo o usuário logado ao salvar.
        """
        serializer.save(tutor=self.request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para criar e gerenciar Agendamentos.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated] # Permissão base

    def get_permissions(self):
        """
        Define permissões específicas para cada ação. Para ver detalhes,
        editar ou apagar, usa a regra customizada.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsAppointmentOwnerOrPetShopOwner]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filtra os agendamentos baseado no tipo de usuário.
        """
        user = self.request.user
        if user.is_superuser:
            return Appointment.objects.all()
        if user.user_type == 'TUTOR':
            return Appointment.objects.filter(tutor=user)
        if user.user_type == 'PROPRIETARIO' and hasattr(user, 'petshop'):
            return Appointment.objects.filter(pet_shop=user.petshop)
        return Appointment.objects.none()

    def perform_create(self, serializer):
        """
        Lógica customizada ao CRIAR um agendamento.
        """
        service = serializer.validated_data.get('service')
        user = self.request.user

        if user.user_type == 'TUTOR':
            pet = serializer.validated_data.get('pet')
            if pet.tutor != user:
                raise serializers.ValidationError("Erro: Você só pode agendar serviços para os seus próprios pets.")
            serializer.save(tutor=user, total_price=service.base_price)

        elif user.user_type == 'PROPRIETARIO':
            if not hasattr(user, 'petshop'):
                 raise serializers.ValidationError("Erro: Você é um proprietário mas não está associado a nenhum pet shop.")
            if service.pet_shop != user.petshop:
                raise serializers.ValidationError("Erro: Você só pode agendar serviços oferecidos pelo seu pet shop.")
            serializer.save(total_price=service.base_price)

        else:
             raise serializers.ValidationError("Erro: Tipo de usuário inválido para criar um agendamento.")