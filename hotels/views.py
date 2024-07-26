# views.py
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import datetime, time, timedelta
from django.utils import timezone
from hotels.models import (Hotel, Service, RoomService,
                           HotelRegisteredUser, AvailableTime, Reservation)
from hotels.forms import CustomUserCreationForm, CustomAuthenticationForm, ReservationForm, RoomServiceRequestForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'hotel_list.html', {'hotels': hotels})


def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    is_registered = False
    if request.user.is_authenticated:
        is_registered = HotelRegisteredUser.objects.filter(
            hotel=hotel,
            private_number=request.user.private_number
        ).exists()

    return render(request, 'hotel_detail.html', {
        'hotel': hotel,
        'is_registered': is_registered
    })


@login_required
def reserve_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # Check if the user is registered at the hotel
    if not HotelRegisteredUser.objects.filter(
            hotel=service.hotel,
            private_number=request.user.private_number
    ).exists():
        return redirect('hotel_detail', hotel_id=service.hotel.id)

    # Generate time slots from 10 AM to 10 PM
    today = timezone.now().date()
    start_time = datetime.combine(today, time(10, 0))
    end_time = datetime.combine(today, time(22, 0))
    delta = timedelta(hours=1)
    time_slots = []

    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time)
        current_time += delta

    # Filter out reserved times
    reserved_times = Reservation.objects.filter(
        service=service,
        reserved_for__start_time__gte=start_time,
        reserved_for__start_time__lt=end_time
    ).values_list('reserved_for__start_time', flat=True)
    reserved_times_set = set(reserved_times)

    available_times = sorted(set(slot for slot in time_slots if slot not in reserved_times_set))

    if request.method == 'POST':
        reservation_time_str = request.POST.get('reservation_time')
        reservation_time = datetime.strptime(reservation_time_str, "%Y-%m-%d %H:%M:%S")

        # Check if the time is available
        if reservation_time in reserved_times_set:
            messages.error(request, 'The selected time is already reserved. Please choose another time.')
        else:
            # Find or create AvailableTime object
            available_time, created = AvailableTime.objects.get_or_create(
                service=service,
                start_time=reservation_time,
                end_time=reservation_time + timedelta(hours=1),
                defaults={'is_reserved': True}
            )
            if created:
                Reservation.objects.create(
                    user=request.user,
                    service=service,
                    reserved_for=available_time
                )
                messages.success(request, 'Service reserved successfully.')
                return redirect('hotel_detail', hotel_id=service.hotel.id)
            else:
                messages.error(request, 'The selected time is no longer available. Please choose another time.')

    return render(request, 'reserve_service.html', {'service': service, 'available_times': available_times})


@login_required
def room_service_request(request, room_service_id):
    room_service = get_object_or_404(RoomService, id=room_service_id)

    # Check if the user is registered at the hotel
    if not HotelRegisteredUser.objects.filter(
            hotel=room_service.hotel,
            private_number=request.user.private_number
    ).exists():
        return redirect('hotel_detail', hotel_id=room_service.hotel.id)

    if request.method == 'POST':
        form = RoomServiceRequestForm(request.POST)
        if form.is_valid():
            room_service_request = form.save(commit=False)
            room_service_request.user = request.user
            room_service_request.room_service = room_service
            room_service_request.save()
            return redirect('hotel_detail', hotel_id=room_service.hotel.id)
    else:
        form = RoomServiceRequestForm()

    return render(request, 'room_service_request.html', {'form': form, 'room_service': room_service})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            private_number = form.cleaned_data.get('private_number')
            email = form.cleaned_data.get('email')
            if HotelRegisteredUser.objects.filter(private_number=private_number, email=email).exists():
                user = form.save()
                login(request, user)
                return redirect('hotel_list')
            else:
                messages.error(request, 'Private number and email not found in the database.')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'login.html'

    def get_success_url(self):
        # Assuming you get the hotel_id from a query parameter or session
        hotel_id = self.request.GET.get('hotel_id')  # Example of retrieving hotel_id from URL query parameters

        if hotel_id:
            return reverse_lazy('hotel_detail', kwargs={'hotel_id': hotel_id})
        else:
            # Default redirection if no hotel_id is provided
            return reverse_lazy('hotel_list')  # Adjust this to your desired default redirect URL


def custom_logout_view(request):
    logout(request)
    return redirect('hotel_list')


# views.py


class UserReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'user_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('-reservation_date')
