# admin.py
from django.contrib import admin
from .models import Hotel, CustomUser, HotelRegisteredUser, Service, AvailableTime, Reservation, RoomService, \
    RoomServiceRequest


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'private_number', 'is_staff', 'is_user')


@admin.register(HotelRegisteredUser)
class HotelRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'private_number', 'email')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price', 'available')


@admin.register(AvailableTime)
class TakenDateAdmin(admin.ModelAdmin):
    list_display = ('service', 'start_time', 'end_time', 'is_reserved')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'reservation_date', 'reserved_for')


@admin.register(RoomService)
class RoomServiceAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'name')


@admin.register(RoomServiceRequest)
class RoomServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'room_service', 'request_date', 'status')
