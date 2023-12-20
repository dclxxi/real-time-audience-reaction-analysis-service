from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import CameraImage


# Create your views here.
def info(request):
    return HttpResponse("live/info 응답")


@csrf_exempt
def cam(request):
    if request.method == 'POST':
        image = request.FILES.get('camera-image')
        CameraImage.objects.create(image=image)
    images = CameraImage.objects.all()
    context = {
        'images': images
    }
    return render(request, 'cam.html', context)


@csrf_exempt
def record(request):
    return render(request, 'record.html')
