# api/serializers.py
from rest_framework import serializers
from .models import User, PetShop, Service, Pet, Appointment,Review, TimeBlock

# Serializer simples para exibir informações básicas do usuário (funcionários)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class PetShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetShop
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    # Usamos o UserSerializer para mostrar os dados dos funcionários, não apenas seus IDs
    performers = UserSerializer(many=True, read_only=True)
    # Campo para receber os IDs dos funcionários ao atualizar um serviço
    performers_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source='performers', write_only=True
    )

    class Meta:
        model = Service
        # Adicionamos os novos campos à lista
        fields = [
            'id', 'name', 'description', 'base_price', 'duration_minutes', 
            'is_active', 'pet_shop', 'performers', 'performers_ids'
        ]

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'
        read_only_fields = ['tutor']

class AppointmentSerializer(serializers.ModelSerializer):
    # Mostra o nome do funcionário em vez de apenas o ID
    employee = UserSerializer(read_only=True)
    # Campo para receber o ID do funcionário ao criar/atualizar
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='employee', write_only=True
    )
    
    class Meta:
        model = Appointment
        # Adicionamos os novos campos à lista
        fields = [
            'id', 'tutor', 'pet', 'pet_shop', 'service', 'client_name', 
            'client_phone', 'employee', 'employee_id', 'appointment_time', 
            'end_time', 'status', 'total_price', 'created_at'
        ]
        read_only_fields = ['tutor', 'status', 'total_price', 'end_time']

class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = '__all__'