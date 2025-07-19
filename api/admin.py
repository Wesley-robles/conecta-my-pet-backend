from django.contrib import admin
from .models import User, PetShop, Pet, Service, Appointment, Review

# Customização para o modelo PetShop no Admin
@admin.register(PetShop)
class PetShopAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de pet shops
    list_display = ('id', 'name', 'owner', 'phone_number')
    
    # Campos que terão um link para a página de edição
    list_display_links = ('id', 'name')
    
    # Adiciona uma barra de busca que procura por nome ou nome de usuário do dono
    search_fields = ('name', 'owner__username')
    
    # Adiciona um filtro na lateral para filtrar por proprietário
    list_filter = ('owner',)

# Registrando os outros modelos da forma simples (eles não precisam de customização por enquanto)
# Note que PetShop não está aqui porque foi registrado com o @admin.register acima
admin.site.register(User)
admin.site.register(Pet)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Review)