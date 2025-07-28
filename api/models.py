from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPE_CHOICES = (
      ("TUTOR", "Tutor"),
      ("PROPRIETARIO", "Proprietário"),
      ("GERENTE", "Gerente"),
      ("FUNCIONARIO", "Funcionário"),
    )
    
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default="TUTOR")
    
    works_at = models.ForeignKey(
        'PetShop',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )

    # --- NOVO CAMPO ADICIONADO ---
    work_schedule = models.JSONField(
        blank=True, 
        null=True, 
        help_text="""
        Ex: 
        {
            "monday": {"start": "08:00", "break_start": "12:00", "break_end": "13:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "break_start": "12:30", "break_end": "13:30", "end": "18:00"}
        }
        """
    )
    # --- FIM DO NOVO CAMPO ---

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
    buffer_time_minutes = models.IntegerField(
        default=0, 
        help_text="Tempo em minutos reservado após o serviço para limpeza/preparação."
    )
    is_active = models.BooleanField(default=True)
    performers = models.ManyToManyField(
        User,
        related_name='performable_services',
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.pet_shop.name}"

#
# Tabela 5: Appointments (Agendamentos)
#
# Em api/models.py

# Em api/models.py

class Appointment(models.Model):
    # --- Definições de Choices ---
    STATUS_CHOICES = (
        ("PENDING", "Pendente"),
        ("CONFIRMED", "Confirmado"),
        ("CANCELLED", "Cancelado"),
        ("COMPLETED", "Concluído"),
    )

    # NOVO: Opções de Frequência para Recorrência
    FREQUENCY_CHOICES = (
        ("WEEKLY", "Semanal"),
        ("BIWEEKLY", "Quinzenal"), # Quinzenal = A cada duas semanas
        ("MONTHLY", "Mensal"),
    )

    # --- Campos do Modelo ---
    tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tutor_appointments')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='appointments')
    pet_shop = models.ForeignKey(PetShop, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    client_name = models.CharField(max_length=150, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='handled_appointments')
    appointment_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # --- NOVOS CAMPOS PARA RECORRÊNCIA ---
    # Estes campos servem apenas para guardar a "regra" no agendamento pai.
    frequency = models.CharField(
        max_length=10, 
        choices=FREQUENCY_CHOICES, 
        blank=True, 
        null=True,
        help_text="Frequência da recorrência (WEEKLY, BIWEEKLY, MONTHLY)"
    )
    recurrence_end_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Data final para a criação de agendamentos recorrentes"
    )
    # Este campo liga todos os "filhos" ao primeiro agendamento da série.
    recurrence_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recurrences'
    )
    # --- FIM DOS NOVOS CAMPOS ---

    def __str__(self):
        try:
            pet_name = self.pet.name
        except Pet.DoesNotExist:
            pet_name = "[Pet Deletado]"
        return f"Agendamento de {pet_name} em {self.pet_shop.name} para {self.appointment_time.strftime('%d/%m/%Y %H:%M')}"
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

class TimeBlock(models.Model):
    """
    Representa um bloqueio de tempo na agenda de um funcionário
    para um compromisso, feriado, etc.
    """
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='time_blocks'
    )
    pet_shop = models.ForeignKey(
        PetShop,
        on_delete=models.CASCADE,
        related_name='time_blocks'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    reason = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Motivo do bloqueio (ex: Consulta médica, Feriado)"
    )

    def __str__(self):
        return f"Bloqueio para {self.employee.username} de {self.start_time.strftime('%H:%M')} a {self.end_time.strftime('%H:%M')}"