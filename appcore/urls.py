from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('assets/', include('assets.urls')),
    path('protocol/', include('protocol.urls')),
    path('locations/', include('locations.api.urls')),
    path ('users/', include('users.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)