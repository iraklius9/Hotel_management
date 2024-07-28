from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from hotels.views import hotel_detail
from django.conf.urls.static import static

urlpatterns = [
    path('', hotel_detail, {'hotel_id': 1}, name='hotel_detail'),
    path('admin/', admin.site.urls),
    path('hotels/', include('hotels.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
