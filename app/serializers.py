from rest_framework import serializers
from .models import Employee, Position, Service, WorkingHours, Appointment, Category, User
from django.utils import timezone
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'phone_number', 'date_joined', 'is_active']
        read_only_fields = ['id', 'date_joined', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)



# ----- Service Serializer -----
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name']


# ----- Working Hours Serializer -----
class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = ['id', 'day', 'start_time', 'end_time']


# ----- Category Serializer -----
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# --- Minimal Employee Info for Position to avoid recursion ---
class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'first_name', 'last_name']


# ----- Position Serializer -----
class PositionSerializer(serializers.ModelSerializer):
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ["id", "position_name_english", "position_name_russian", "position_name_uzbek", "kpi_postion_id", "employees"]

    def get_employees(self, obj):
        employees = obj.employees.filter(is_available=True)
        return SimpleEmployeeSerializer(employees, many=True).data


# ----- Short Employee Serializer -----
class EmployeeShortSerializer(serializers.ModelSerializer):
    position_kpi_id = serializers.SerializerMethodField()
    position_data = PositionSerializer(source='position', read_only=True)
    working_hours = WorkingHoursSerializer(many=True, read_only=True)
    services_data = ServiceSerializer(source='services', many=True, read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'image', 'price',
            'description', 'experience', 'services_data', 'certificates',
            'is_available', 'working_hours', 'position', 'position_kpi_id', 'position_data', 'employee_kpi_id'
        ]

    def get_position_kpi_id(self, obj):
        if obj.position:
            return obj.position.kpi_postion_id
        return None


# ----- Full Employee Serializer -----
class EmployeeSerializer(serializers.ModelSerializer):
    services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all())
    working_hours = serializers.PrimaryKeyRelatedField(many=True, queryset=WorkingHours.objects.all())
    kpi_postion_id = serializers.IntegerField()
    position_data = PositionSerializer(source='position', read_only=True)
    position_kpi_id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone', 'image',
            'price', 'description', 'experience', 'services',
            'certificates', 'is_available', 'working_hours',
            'kpi_postion_id', 'position_data', 'position_kpi_id', 'employee_kpi_id'
        ]

    def get_position_kpi_id(self, obj):
        if obj.position:
            return obj.position.kpi_postion_id
        return None

    def create(self, validated_data):
        kpi_id = validated_data.pop('kpi_postion_id')
        try:
            position = Position.objects.get(kpi_postion_id=kpi_id)
        except Position.DoesNotExist:
            raise serializers.ValidationError({"kpi_postion_id": "Position with this KPI ID not found."})
        validated_data['position'] = position
        validated_data['kpi_postion_id'] = kpi_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        kpi_id = validated_data.pop('kpi_postion_id', None)
        if kpi_id is not None:
            try:
                position = Position.objects.get(kpi_postion_id=kpi_id)
                instance.position = position
                instance.kpi_postion_id = kpi_id
            except Position.DoesNotExist:
                raise serializers.ValidationError({"kpi_postion_id": "Position with this KPI ID not found."})
        return super().update(instance, validated_data)


# ----- Appointment Serializer -----
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_date(self, value):
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError("Appointment time must be in the future.")
        return value