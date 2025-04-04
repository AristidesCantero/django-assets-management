from django.contrib import admin
from locations.models import Business, Headquarters, InternalLocation


# Register your models here.
admin.site.register(Business)
admin.site.register(Headquarters)
admin.site.register(InternalLocation)