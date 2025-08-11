from pyexpat import model
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from pytz import timezone



class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

class Service(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField(default=0)


class Position(models.Model):
    position_name_english = models.CharField(max_length=100)
    position_name_russian = models.CharField(max_length=100)
    position_name_uzbek = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="positions", null=True, blank=True)
    kpi_postion_id = models.PositiveBigIntegerField(default=0, unique=True)  # KPI ID
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.position_name_english}"


class WorkingHours(models.Model):
    WEEKDAYS = [
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ]

    day = models.CharField(max_length=3, choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_display()}: {self.start_time} - {self.end_time}"
        
    class Meta:
        ordering = ['day', 'start_time']


class Employee(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, null=True, blank=True)
    image = models.ImageField(upload_to="employer_images", blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    services = models.ManyToManyField('Service', null=True, blank=True)
    certificates = models.CharField(max_length=200)
    is_available = models.BooleanField(default=True)
    working_hours = models.ManyToManyField('WorkingHours', related_name='employees')

    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        related_name='employees',
        null=True,
        blank=True
    )

    kpi_postion_id = models.PositiveBigIntegerField()
    employee_kpi_id = models.PositiveBigIntegerField(unique=True)

    def __str__(self):
        return self.email


class Appointment(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateTimeField()
    doctor = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='appointments')
    additional_info = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    calendly_uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname} - {self.date}"

    def clean(self):
        super().clean()
        if self.date < timezone.now():
            raise ValidationError({'date': 'Appointment time is not valid'})