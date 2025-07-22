# api/views.py
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, PetShop, Service, Pet, Appointment
from .serializers import (
    PetShopSerializer, ServiceSerializer, PetSerializer, AppointmentSerializer
)
from .permissions import CanManagePetShop, IsAppointmentOwnerOrPetShopOwner
from datetime import timedelta

class PetShopViewSet(viewsets.ModelViewSet):
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer
    permission_classes = [IsAuthenticated]

class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [CanManagePetShop]

    def get_queryset(self):
        petshop_pk = self.kwargs['petshop_pk']
        return Service.objects.filter(pet_shop_id=petshop_pk)

class PetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(tutor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(tutor=self.request.user)

# Em api/views.py

class AppointmentViewSet(viewsets.ModelViewSet):
    # --- Início do Bloco da Classe ---
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'confirm', 'cancel']:
            self.permission_classes = [IsAuthenticated, IsAppointmentOwnerOrPetShopOwner]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Appointment.objects.all()
        if user.user_type == 'TUTOR':
            return Appointment.objects.filter(tutor=user)
        if user.user_type == 'PROPRIETARIO':
            owned_petshops = PetShop.objects.filter(owner=user)
            return Appointment.objects.filter(pet_shop__in=owned_petshops)
        if user.user_type in ['GERENTE', 'FUNCIONARIO']:
            if user.works_at:
                return Appointment.objects.filter(pet_shop=user.works_at)
        return Appointment.objects.none()

    # ESTE MÉTODO PRECISA ESTAR DENTRO DA CLASSE, COM ESTE RECUO
   # Em api/views.py, dentro da classe AppointmentViewSet

def perform_create(self, serializer):
    user = self.request.user
    service = serializer.validated_data.get('service')
    employee = serializer.validated_data.get('employee') # O funcionário vem da requisição
    appointment_time = serializer.validated_data.get('appointment_time')

    # Validação 1: O funcionário escolhido realmente pode realizar este serviço?
    if employee not in service.performers.all():
        raise serializers.ValidationError(
            f"O funcionário {employee.username} não está habilitado para realizar o serviço de {service.name}."
        )

    # Validação 2: Validação de conflito de horário PARA O FUNCIONÁRIO
    duration = service.duration_minutes or 60
    end_time = appointment_time + timedelta(minutes=duration)

    conflicting_appointments = Appointment.objects.filter(
        employee=employee, # A verificação agora é por funcionário
        status__in=['CONFIRMED', 'PENDING'], # Verifica contra agendamentos pendentes ou confirmados
        appointment_time__lt=end_time,
        end_time__gt=appointment_time
    )

    if conflicting_appointments.exists():
        raise serializers.ValidationError(
            f"Conflito de horário. O funcionário {employee.username} já está ocupado neste período."
        )

    # A lógica de quem pode criar continua a mesma, mas o salvamento muda
    if user.user_type == 'TUTOR':
        pet = serializer.validated_data.get('pet')
        if pet.tutor != user:
            raise serializers.ValidationError("Erro: Você só pode agendar serviços para os seus próprios pets.")
        serializer.save(tutor=user, total_price=service.base_price, end_time=end_time)
    
    elif user.user_type in ['PROPRIETARIO', 'GERENTE', 'FUNCIONARIO']:
        # A validação de permissão da loja já foi feita na lógica acima
        serializer.save(total_price=service.base_price, end_time=end_time)
    
    else:
         raise serializers.ValidationError("Erro: Tipo de usuário inválido para criar um agendamento.")
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        appointment = self.get_object()
        user = request.user
        allowed_roles = ['PROPRIETARIO', 'GERENTE', 'FUNCIONARIO']
        if user.user_type not in allowed_roles:
            return Response(
                {'detail': 'Apenas a equipe do pet shop pode confirmar agendamentos.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'CONFIRMED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        user = request.user
        is_tutor_owner = (user.user_type == 'TUTOR' and appointment.tutor == user)
        is_shop_staff = user.user_type in ['PROPRIETARIO', 'GERENTE', 'FUNCIONARIO']
        if not (is_tutor_owner or is_shop_staff):
            return Response(
                {'detail': 'Você não tem permissão para cancelar este agendamento.'},
                status=status.HTTP_403_FORBIDDEN
            )
        appointment.status = 'CANCELLED'
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    # --- Fim do Bloco da Classe ---