from rest_framework import serializers
# Certifique-se de que todos os modelos estão importados
from .models import PetShop, Service, Pet, Appointment

class PetShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetShop
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        # Lembre-se que renomeamos o campo 'price' para 'base_price' no modelo.
        # O serializer lida com isso automaticamente.
        fields = '__all__'

# VERIFIQUE SE ESTA CLASSE EXISTE E ESTÁ ESCRITA CORRETAMENTE
class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = '__all__'
        read_only_fields = ['tutor']

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['tutor', 'status', 'total_price']