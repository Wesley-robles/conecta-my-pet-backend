# api/views.py
from datetime import timedelta, datetime
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import User, PetShop, Service, Pet, Appointment, Review, TimeBlock
from .serializers import (
    PetShopSerializer, ServiceSerializer, PetSerializer, AppointmentSerializer, TimeBlockSerializer
)


from .models import User, PetShop, Service, Pet, Appointment
from .serializers import (
    PetShopSerializer, ServiceSerializer, PetSerializer, AppointmentSerializer
)
from .permissions import CanManagePetShop, IsAppointmentOwnerOrPetShopOwner


class PetShopViewSet(viewsets.ModelViewSet):
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer
    permission_classes = [IsAuthenticated]

   # Em api/views.py, dentro da classe PetShopViewSet

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        petshop = self.get_object()
        date_str = request.query_params.get('date')
        service_id = request.query_params.get('service_id')

        if not date_str or not service_id:
            return Response(
                {'detail': 'A data (no formato AAAA-MM-DD) e o ID do serviço (service_id) são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            day = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.objects.get(pk=service_id, pet_shop=petshop)
        except (ValueError, Service.DoesNotExist):
            return Response({'detail': 'Data inválida ou serviço não encontrado neste pet shop.'}, status=status.HTTP_400_BAD_REQUEST)

        performers = service.performers.all()
        if not performers.exists():
            return Response([], status=status.HTTP_200_OK)

        # Busca agendamentos E bloqueios existentes para estes funcionários neste dia
        existing_appointments = Appointment.objects.filter(
            employee__in=performers, appointment_time__date=day, status__in=['CONFIRMED', 'PENDING']
        )
        # --- NOVA LÓGICA ABAIXO ---
        existing_blocks = TimeBlock.objects.filter(
            employee__in=performers, start_time__date=day
        )

        total_duration = timedelta(minutes=(service.duration_minutes + service.buffer_time_minutes))
        day_of_week = day.strftime('%A').lower()
        available_slots = []
        
        slot_interval_minutes = 15
        day_start_time = datetime.strptime("08:00", "%H:%M").time()
        day_end_time = datetime.strptime("20:00", "%H:%M").time()

        slot_time = datetime.combine(day, day_start_time)
        end_of_day = datetime.combine(day, day_end_time)
        end_of_day_aware = timezone.make_aware(end_of_day)

        while slot_time < end_of_day:
            slot_start_aware = timezone.make_aware(slot_time)
            slot_end_aware = slot_start_aware + total_duration

            if slot_end_aware > end_of_day_aware:
                break

            is_slot_available = False
            for performer in performers:
                performer_is_free = True
                
                schedule = performer.work_schedule.get(day_of_week) if performer.work_schedule else None
                if not schedule:
                    performer_is_free = False
                    continue

                work_start = datetime.strptime(schedule['start'], '%H:%M').time()
                break_start = datetime.strptime(schedule['break_start'], '%H:%M').time()
                break_end = datetime.strptime(schedule['break_end'], '%H:%M').time()
                work_end = datetime.strptime(schedule['end'], '%H:%M').time()

                fits_in_morning = (slot_start_aware.time() >= work_start and slot_end_aware.time() <= break_start)
                fits_in_afternoon = (slot_start_aware.time() >= break_end and slot_end_aware.time() <= work_end)

                if not (fits_in_morning or fits_in_afternoon):
                    performer_is_free = False
                    continue

                # Verifica conflito com agendamentos
                for appt in existing_appointments:
                    if appt.employee == performer:
                        if slot_start_aware < appt.end_time and slot_end_aware > appt.appointment_time:
                            performer_is_free = False
                            break
                if not performer_is_free: continue

                # --- NOVA LÓGICA ABAIXO ---
                # Verifica conflito com bloqueios
                for block in existing_blocks:
                    if block.employee == performer:
                        if slot_start_aware < block.end_time and slot_end_aware > block.start_time:
                            performer_is_free = False
                            break
                if not performer_is_free: continue
                
                if performer_is_free:
                    is_slot_available = True
                    break
            
            if is_slot_available:
                available_slots.append(slot_time.strftime('%H:%M'))

            slot_time += timedelta(minutes=slot_interval_minutes)

        return Response(available_slots)

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


class AppointmentViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        user = self.request.user
        service = serializer.validated_data.get('service')
        employee = serializer.validated_data.get('employee')
        appointment_time = serializer.validated_data.get('appointment_time')
        target_petshop = serializer.validated_data.get('pet_shop')

        # Lógica de Validação de Horário
        duration = service.duration_minutes or 60
        end_time = appointment_time + timedelta(minutes=(duration + service.buffer_time_minutes))
        if not employee.work_schedule:
            raise serializers.ValidationError(f"O funcionário {employee.username} não tem um horário de trabalho definido.")
        day_of_week = appointment_time.strftime('%A').lower()
        schedule_for_day = employee.work_schedule.get(day_of_week)
        if not schedule_for_day:
            raise serializers.ValidationError(f"O funcionário {employee.username} não trabalha neste dia da semana.")
        work_start = datetime.strptime(schedule_for_day['start'], '%H:%M').time()
        break_start = datetime.strptime(schedule_for_day['break_start'], '%H:%M').time()
        break_end = datetime.strptime(schedule_for_day['break_end'], '%H:%M').time()
        work_end = datetime.strptime(schedule_for_day['end'], '%H:%M').time()
        appointment_start_time = appointment_time.time()
        appointment_end_time = end_time.time()
        fits_in_morning_shift = (appointment_start_time >= work_start and appointment_end_time <= break_start)
        fits_in_afternoon_shift = (appointment_start_time >= break_end and appointment_end_time <= work_end)
        if not (fits_in_morning_shift or fits_in_afternoon_shift):
            raise serializers.ValidationError("O horário solicitado não se encaixa nos turnos de trabalho ou conflita com o intervalo.")

        # Lógica de Validação de Conflito
        conflicting_appointments = Appointment.objects.filter(
            employee=employee, status__in=['CONFIRMED', 'PENDING'], appointment_time__lt=end_time, end_time__gt=appointment_time
        )
        if conflicting_appointments.exists():
            raise serializers.ValidationError(f"Conflito de horário. O funcionário {employee.username} já está ocupado neste período.")

        # Lógica de Permissão de Criação e Salvamento
        if user.user_type == 'TUTOR':
            pet = serializer.validated_data.get('pet')
            if pet.tutor != user:
                raise serializers.ValidationError("Erro: Você só pode agendar serviços para os seus próprios pets.")
            serializer.save(tutor=user, total_price=service.base_price, end_time=end_time)
        elif user.user_type in ['PROPRIETARIO', 'GERENTE', 'FUNCIONARIO']:
            if service.pet_shop != target_petshop:
                raise serializers.ValidationError("Erro: Este serviço não pertence ao pet shop selecionado.")
            if user.user_type == 'PROPRIETARIO':
                if target_petshop not in user.petshops.all():
                    raise serializers.ValidationError("Erro: Você só pode agendar em um pet shop que você possui.")
            else:
                if target_petshop != user.works_at:
                    raise serializers.ValidationError("Erro: Você só pode agendar no pet shop onde trabalha.")
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
    
class TimeBlockViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerir bloqueios de tempo na agenda.
    Apenas Proprietários e Gerentes podem gerir bloqueios.
    """
    serializer_class = TimeBlockSerializer
    # A permissão será customizada abaixo
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra os bloqueios para mostrar apenas os relevantes
        para o usuário logado (baseado nas suas lojas).
        """
        user = self.request.user
        if user.is_superuser:
            return TimeBlock.objects.all()

        petshops = []
        if user.user_type == 'PROPRIETARIO':
            petshops = user.petshops.all()
        elif user.user_type in ['GERENTE', 'FUNCIONARIO']:
            if user.works_at:
                petshops = [user.works_at]

        return TimeBlock.objects.filter(pet_shop__in=petshops)

    def perform_create(self, serializer):
        """
        Valida se o usuário tem permissão para criar um bloqueio
        para o funcionário e a loja selecionados.
        """
        user = self.request.user
        employee = serializer.validated_data.get('employee')
        pet_shop = serializer.validated_data.get('pet_shop')

        # Regra: Apenas um Proprietário ou Gerente pode criar bloqueios
        if user.user_type not in ['PROPRIETARIO', 'GERENTE']:
            raise serializers.ValidationError("Apenas Proprietários ou Gerentes podem criar bloqueios de horário.")

        # Regra: O funcionário a ser bloqueado deve pertencer à loja correta
        if employee.works_at != pet_shop:
             raise serializers.ValidationError("Este funcionário não trabalha no pet shop selecionado.")

        # Regra: O criador do bloqueio deve gerir aquela loja
        if user.user_type == 'PROPRIETARIO':
            if pet_shop not in user.petshops.all():
                raise serializers.ValidationError("Você só pode criar bloqueios para pet shops que você possui.")
        elif user.user_type == 'GERENTE':
            if pet_shop != user.works_at:
                raise serializers.ValidationError("Você só pode criar bloqueios para o pet shop onde trabalha.")

        serializer.save()