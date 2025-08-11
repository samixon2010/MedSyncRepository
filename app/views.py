from django.views import View
from rest_framework import generics, status
from rest_framework.generics import GenericAPIView, CreateAPIView
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Category, Position, Employee, Service, WorkingHours, Appointment, User
from .serializers import (
    CategorySerializer,
    PositionSerializer,
    EmployeeSerializer,
    ServiceSerializer,
    WorkingHoursSerializer,
    AppointmentSerializer,
    LoginSerializer,
    UserSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.dateparse import parse_datetime
from django.conf import settings
from django.utils.decorators import method_decorator
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate



CALENDLY_TOKEN = """eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzU0NDYyODIwLCJqdGkiOiI0MDFhYTA4MC1kMjgxLTRhNzgtYjI0OC00YzQ1Mzc0MmQ2YmEiLCJ1c2VyX3V1aWQiOiJjNDNkM2EwNC1jN2VjLTRmYzEtYjUzMC02NTFmZTc5OTM1ZmEifQ.Bif20v8c61uRVoHsJsEVBn1PHLaVc9108H06Tod0RbIg8rI1_TZVBReSP1MacL75sAXg0k5_6xaDz3NxwWYOHw"""

@csrf_exempt
def webhook_receiver(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)

            event_type = payload.get("event")

            event_data = payload.get("payload", {})

            uuid = event_data.get("uuid")
            name = event_data.get("name", "")
            email = event_data.get("email", "")
            phone = event_data.get("text_reminder_number", "")
            start_time = event_data.get("scheduled_event", {}).get("start_time")

            date_obj = parse_datetime(start_time)

            doctor = Employee.objects.first()

            if event_type == "invitee.created":
                Appointment.objects.create(
                    name=name,
                    surname="",
                    phone=phone or "",
                    email=email,
                    date=date_obj,
                    doctor=doctor,
                    additional_info="From Calendly",
                    calendly_uuid=uuid
                )
            elif event_type == "invitee.canceled":
                Appointment.objects.filter(calendly_uuid=uuid).delete()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    return JsonResponse({"status": "only POST allowed"}, status=405)


class calendlyAvailabilityView(View):
    def get(self, request):
        start_time = request.GET.get('start')
        end_time = request.GET.get('end')

        if not start_time or not end_time:
            return JsonResponse({"error": "Missing required parameters."}, status=400)

        url = "https://api.calendly.com/user_busy_times"
        headers = {
            "Authorization": f"Bearer {CALENDLY_TOKEN}",
            "Content-Type": "application/json"
        }
        params = {
            "start_time": start_time,
            "end_time": end_time,
            "user" : "https://api.calendly.com/users/c43d3a04-c7ec-4fc1-b530-651fe79935fa"
        }

        response = requests.get(url, headers=headers, params=params)
        return JsonResponse(response.json(), status=response.status_code)
    


@method_decorator(csrf_exempt, name='dispatch')
class CalendlyAvailabilityScheduleView(View):
    def get(self, request):

        url = "https://api.calendly.com/user_availability_schedules/8ac6d4b4-b068-4155-8de0-3f2a4aa738f4"
        headers = {
            "Authorization": f"Bearer {CALENDLY_TOKEN}",
            "Content-Type": "application/json",
            "user" : "https://api.calendly.com/users/c43d3a04-c7ec-4fc1-b530-651fe79935fa"
        }

        response = requests.get(url, headers=headers)
        return JsonResponse(response.json(), status=response.status_code)


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                })
            return Response({'msg': 'Email or password is incorrect!!'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----- CRUD API views with permissions -----
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class PositionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Position.objects.filter(is_active=True)
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]


class PositionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Position.objects.filter(is_active=True)
    serializer_class = PositionSerializer
    lookup_field = 'kpi_postion_id'
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class EmployeesListCreateAPIView(generics.ListCreateAPIView):
    queryset = Employee.objects.filter(is_available=True)
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]


class EmployeesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.filter(is_available=True)
    serializer_class = EmployeeSerializer
    lookup_field = 'employee_kpi_id'
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_available = False
        instance.save()


class ServicesListCreateAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]


class ServicesRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]


class WorkingHoursListCreateView(generics.ListCreateAPIView):
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    permission_classes = [IsAuthenticated]


class WorkingHoursDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkingHours.objects.all()
    serializer_class = WorkingHoursSerializer
    permission_classes = [IsAuthenticated]


class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.filter(is_available=True)
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.filter(is_available=True)
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        instance.is_available = False
        instance.save()