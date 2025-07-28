# api/serializers.py
from rest_framework import serializers
from .models import User, PetShop, Service, Pet, Appointment, Review, TimeBlock

# Serializer simples para exibir informações básicas de usuários (funcionários, tutores, etc.)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'user_type']

class PetShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetShop
        fields = '__all__'

class PetSerializer(serializers.ModelSerializer):
    tutor = UserSerializer(read_only=True)

    class Meta:
        model = Pet
        fields = '__all__'
        read_only_fields = ['tutor']

class ServiceSerializer(serializers.ModelSerializer):
    # Para exibir os dados dos funcionários, não apenas seus IDs
    performers = UserSerializer(many=True, read_only=True)
    # Campo para receber os IDs dos funcionários ao criar/atualizar um serviço
    performers_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, source='performers', write_only=True, required=False
    )

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'base_price', 'duration_minutes', 
            'buffer_time_minutes', 'is_active', 'pet_shop', 'performers', 'performers_ids'
        ]

# Em api/serializers.py

class AppointmentSerializer(serializers.ModelSerializer):
    # Campos para LEITURA (mostrar dados completos)
    tutor = UserSerializer(read_only=True)
    pet = PetSerializer(read_only=True)
    pet_shop = PetShopSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    employee = UserSerializer(read_only=True)

    # Campos para ESCRITA (receber apenas os IDs)
    pet_id = serializers.PrimaryKeyRelatedField(
        queryset=Pet.objects.all(), source='pet', write_only=True
    )
    pet_shop_id = serializers.PrimaryKeyRelatedField(
        queryset=PetShop.objects.all(), source='pet_shop', write_only=True
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), source='service', write_only=True
    )
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='employee', write_only=True
    )

    class Meta:
        model = Appointment
        fields = '__all__' # Inclui todos os campos
        read_only_fields = ('status', 'total_price', 'end_time', 'recurrence_parent', 'tutor')

    def validate(self, data):
        # ... (a sua lógica de validação existente aqui, se houver)
        return data

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('tutor',)

class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = '__all__'