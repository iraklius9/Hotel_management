# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    private_number = models.CharField(max_length=20, unique=True)
    bank_card = models.CharField(max_length=16, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'private_number']

    def __str__(self):
        return self.private_number


class HotelRegisteredUser(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    private_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.private_number


class Service(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AvailableTime(models.Model):
    service = models.ForeignKey(Service, related_name='available_times', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_reserved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.service.name} from {self.start_time} to {self.end_time}"


class Reservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    reserved_for = models.ForeignKey(AvailableTime, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.service} on {self.reserved_for.start_time}"


class RoomService(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='room_services', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class RoomServiceRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room_service = models.ForeignKey(RoomService, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')],
                              default='Pending')

    def __str__(self):
        return f"{self.user} - {self.room_service} on {self.request_date}"
