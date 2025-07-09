from django.db import models
from django.contrib.auth.models import AbstractUser

#
# Tabela 1: Users (Usuários)
# Vamos estender o usuário padrão do Django para adicionar nossos campos.
# Esta é a melhor prática para segurança e autenticação.
#
class User(AbstractUser):
    USER_TYPE_CHOICES = (
      ("TUTOR", "Tutor"),
      ("PROPRIETARIO", "Proprietário"), # <-- MUDANÇA AQUI
    )
    # Campos que o User padrão não tem:
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default="TUTOR") # Aumentei o max_length para segurança

    def __str__(self):
        return self.username

#
# Tabela 2: PetShops
#
class PetShop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='petshops')
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    opening_hours = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#
# Tabela 3: Pets
#
class Pet(models.Model):
    SIZE_CHOICES = (
      ("PEQUENO", "Pequeno"),
      ("MEDIO", "Médio"),
      ("GRANDE", "Grande"),
    )
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50, blank=True, null=True)
    breed = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True) # Para alergias, cuidados, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.tutor.username})"

#
# Tabela 4: Services (Serviços)
#
class Service(models.Model):
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.pet_shop.name}"

#
# Tabela 5: Appointments (Agendamentos)
#
class Appointment(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pendente"),
        ("CONFIRMED", "Confirmado"),
        ("CANCELLED", "Cancelado"),
        ("COMPLETED", "Concluído"),
    )
    tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_appointments')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    client_name = models.CharField(max_length=150, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Agendamento de {self.pet.name} em {self.pet_shop.name} para {self.appointment_time.strftime('%d/%m/%Y %H:%M')}"

#
# Tabela 6: Reviews (Avaliações)
#
class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField() # Nota de 1 a 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.tutor.username} para {self.pet_shop.name} - Nota: {self.rating}"