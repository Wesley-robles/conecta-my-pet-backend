from rest_framework import serializers
from .models import PetShop, Service

class PetShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetShop
        fields = '__all__' # Por enquanto, vamos incluir todos os campos do modelo.

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'