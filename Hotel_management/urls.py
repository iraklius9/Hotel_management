from django.contrib import admin
from django.urls import path, include

from hotels.views import hotel_list

urlpatterns = [
    path('', hotel_list, name='hotel_list'),
    path('admin/', admin.site.urls),
    path('hotels/', include('hotels.urls')),

]
