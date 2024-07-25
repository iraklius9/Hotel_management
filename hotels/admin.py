from django.contrib import admin
from hotels.models import Hotel, Service, Reservation, RoomService, RoomServiceRequest, CustomUser, HotelRegisteredUser

admin.site.register(Hotel)
admin.site.register(Service)
admin.site.register(Reservation)
admin.site.register(RoomService)
admin.site.register(RoomServiceRequest)
admin.site.register(CustomUser)
admin.site.register(HotelRegisteredUser)
