# views.py
from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware

from hotels.models import (Hotel, Service, RoomService,
                           HotelRegisteredUser, AvailableTime, Reservation)
from hotels.forms import CustomUserCreationForm, CustomAuthenticationForm, ReservationForm, RoomServiceRequestForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal


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

    if not HotelRegisteredUser.objects.filter(
            hotel=service.hotel,
            private_number=request.user.private_number
    ).exists():
        return redirect('hotel_detail', hotel_id=service.hotel.id)

    today = timezone.now().date()
    start_time = datetime.combine(today, time(10, 0))
    end_time = datetime.combine(today, time(21, 0))
    delta = timedelta(hours=1)
    time_slots = []

    current_time = make_aware(start_time)
    end_time = make_aware(end_time)
    while current_time <= end_time:
        time_slots.append(current_time)
        current_time += delta

    now = timezone.now()
    reserved_times = Reservation.objects.filter(
        service=service,
        reserved_for__start_time__gte=start_time,
        reserved_for__start_time__lt=end_time + timedelta(hours=1)
    ).values_list('reserved_for__start_time', flat=True)
    reserved_times_set = set(reserved_times)

    available_times = sorted(slot for slot in time_slots
                             if slot not in reserved_times_set and slot > now)

    no_times_message = None
    if not available_times:
        no_times_message = "All available times for today are reserved."

    if request.method == 'POST':
        reservation_times_str = request.POST.getlist('reservation_times')
        reservation_times = [make_aware(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")) for time_str in
                             reservation_times_str]

        total_hours = len(reservation_times)
        service_price = Decimal(service.price)
        total_price = service_price * total_hours
        discount_price = total_price * Decimal('0.8')

        conflict_times = [time for time in reservation_times if time in reserved_times_set]
        if conflict_times:
            messages.error(request,
                           f'The following times are already reserved: {", ".join([time.strftime("%Y-%m-%d %H:%M") for time in conflict_times])}. Please choose different times.')
        elif any(time <= now for time in reservation_times):
            messages.error(request, 'Some of the selected times are in the past. Please choose future times.')
        else:
            for reservation_time in reservation_times:
                available_time = AvailableTime.objects.filter(
                    service=service,
                    start_time=reservation_time,
                    end_time=reservation_time + timedelta(hours=1)
                ).first()

                if available_time:
                    available_time.is_reserved = True
                    available_time.save()
                else:
                    available_time = AvailableTime.objects.create(
                        service=service,
                        start_time=reservation_time,
                        end_time=reservation_time + timedelta(hours=1),
                        is_reserved=True
                    )

                if not Reservation.objects.filter(
                        user=request.user,
                        service=service,
                        reserved_for=available_time
                ).exists():
                    Reservation.objects.create(
                        user=request.user,
                        service=service,
                        reserved_for=available_time
                    )

            messages.success(request, f'Service reserved successfully. Total cost: ${discount_price:.2f}')
            return redirect('reserve_service', service_id=service.id)

    return render(request, 'reserve_service.html', {
        'service': service,
        'available_times': available_times,
        'no_times_message': no_times_message
    })


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
