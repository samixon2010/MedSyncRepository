from django.urls import path
from .views import (
    CategoryListCreateAPIView, CategoryRetrieveUpdateDestroyAPIView, LoginView,
    PositionListCreateAPIView, PositionRetrieveUpdateDestroyAPIView,
    EmployeesListCreateAPIView, EmployeesRetrieveUpdateDestroyAPIView,
    ServicesListCreateAPIView, ServicesRetrieveUpdateDestroyAPIView,
    WorkingHoursListCreateView, WorkingHoursDetailView,
    AppointmentDetailView, AppointmentListCreateView, webhook_receiver, calendlyAvailabilityView, CalendlyAvailabilityScheduleView,
    RegisterView
)

urlpatterns = [
    # Category
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail'),

    # Position
    path('positions/', PositionListCreateAPIView.as_view(), name='position-list-create'),
    path('positions/<int:kpi_postion_id>/', PositionRetrieveUpdateDestroyAPIView.as_view(), name='position-detail'),

    # Employer 
    path('employees/', EmployeesListCreateAPIView.as_view(), name='employees-list-create'),
    path('employees/<int:employee_kpi_id>/', EmployeesRetrieveUpdateDestroyAPIView.as_view(), name='employees-detail'),

    # Services 
    path('services/', ServicesListCreateAPIView.as_view(), name='services-list-create'),
    path('services/<int:pk>/', ServicesRetrieveUpdateDestroyAPIView.as_view(), name='service-detail'), 

    #Working hours

    path('working_hours/', WorkingHoursListCreateView.as_view(), name='workinh-hours-list-create'),
    path('working_hours/<int:pk>/', WorkingHoursDetailView.as_view(), name='workinh-hours-detail'),
    
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),

    path('webhook/', webhook_receiver, name='webhook'),
    path('calenlyBusyTimeView/', calendlyAvailabilityView.as_view()),
    path('calendlyAvailabilitySchedule/', CalendlyAvailabilityScheduleView.as_view()),

    # register & login
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
]