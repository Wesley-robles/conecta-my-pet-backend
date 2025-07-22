# api/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PetShop, Pet, Service, Appointment, Review

# --- CUSTOMIZAÇÃO PARA USER ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'works_at', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('user_type', 'works_at', 'is_staff', 'is_superuser', 'groups')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('user_type', 'phone_number', 'birth_date', 'works_at')}),
    )

# --- CUSTOMIZAÇÃO PARA PETSHOP ---
@admin.register(PetShop)
class PetShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'phone_number')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'owner__username')
    list_filter = ('owner',)
    fieldsets = (
        ('Informações Principais', {
            'fields': ('name', 'owner', 'description')
        }),
        ('Contato e Endereço', {
            'fields': ('phone_number', 'address', ('latitude', 'longitude'))
        }),
        ('Horários de Funcionamento', {
            'fields': ('opening_hours',),
            'classes': ('collapse',)
        }),
    )

# --- CUSTOMIZAÇÃO PARA SERVICE ---
# Em api/admin.py

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'pet_shop', 'base_price', 'duration_minutes', 'is_active')
    search_fields = ('name', 'description', 'pet_shop__name')
    list_filter = ('pet_shop', 'is_active')
    filter_horizontal = ('performers',)
    
    # A CORREÇÃO ESTÁ AQUI
    fieldsets = (
        (None, {
            # Adicionamos 'performers' a esta lista de campos
            'fields': ('pet_shop', 'name', 'description', 'performers')
        }),
        ('Detalhes do Preço e Duração', {
            'fields': ('base_price', 'duration_minutes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

# --- CUSTOMIZAÇÃO PARA PET ---
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'tutor', 'get_tutor_phone', 'species', 'breed')
    search_fields = ('name', 'tutor__username', 'tutor__email', 'breed')
    list_filter = ('species', 'breed', 'tutor')

    @admin.display(description='Telefone do Tutor')
    def get_tutor_phone(self, obj):
        if obj.tutor:
            return obj.tutor.phone_number
        return "N/A"

# --- CUSTOMIZAÇÃO PARA APPOINTMENT ---
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'pet', 'tutor', 'pet_shop', 'service', 'appointment_time', 'status')
    search_fields = ('pet__name', 'tutor__username', 'pet_shop__name', 'service__name')
    list_filter = ('status', 'pet_shop', 'tutor')
    list_per_page = 20

# --- NOVA CUSTOMIZAÇÃO PARA REVIEW ---
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de avaliações
    list_display = ('pet_shop', 'tutor', 'rating', 'created_at')
    
    # Adiciona filtros na lateral
    list_filter = ('rating', 'pet_shop')
    
    # Adiciona uma barra de busca
    search_fields = ('pet_shop__name', 'tutor__username', 'comment')
    
    # Define campos como somente leitura (não editáveis) na página de edição
    readonly_fields = ('created_at',)

# A lista de registro simples agora está vazia, pois TODOS os nossos modelos
# principais foram registrados com a anotação @admin.register