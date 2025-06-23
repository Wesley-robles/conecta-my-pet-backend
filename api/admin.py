from django.contrib import admin
from .models import User, PetShop, Pet, Service, Appointment, Review

# Registrando os modelos para que apareçam no painel de administração
admin.site.register(User)
admin.site.register(PetShop)
admin.site.register(Pet)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Review)