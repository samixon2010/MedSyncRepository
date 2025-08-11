from django.contrib import admin
from .models import Service, Category, Position, WorkingHours, Employee, Appointment

# Register your models here.

admin.site.register(Service)
admin.site.register(Category)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(WorkingHours)
admin.site.register(Appointment)