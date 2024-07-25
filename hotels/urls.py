from django.urls import path
from .views import hotel_list, hotel_detail, reserve_service, room_service_request, register, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', hotel_list, name='hotel_list'),
    path('hotels/<int:hotel_id>/', hotel_detail, name='hotel_detail'),
    path('reserve/<int:service_id>/', reserve_service, name='reserve_service'),
    path('room_service_request/<int:room_service_id>/', room_service_request, name='room_service_request'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
