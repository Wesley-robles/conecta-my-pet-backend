# api/urls.py
from django.urls import path
from .views import PetShopListView

urlpatterns = [
    path('petshops/', PetShopListView.as_view(), name='petshop-list'),
]