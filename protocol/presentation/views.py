from django.shortcuts import render

from protocol.domain.models import maintenanceRoutine

# Create your views here.

def protocolHome(request):
    routines = maintenanceRoutine.objects.all()
    context = {
        'routines': routines
    }
    return render('protocol/protocolHome.html', context)