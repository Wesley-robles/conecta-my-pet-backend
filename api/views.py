from django.shortcuts import render
from rest_framework import generics
from .models import PetShop
from .serializers import PetShopSerializer

class PetShopListView(generics.ListAPIView):
    queryset = PetShop.objects.all()
    serializer_class = PetShopSerializer