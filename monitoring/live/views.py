from django.http import HttpResponse
from django.shortcuts import render

from live.models import CameraImage


# Create your views here.
def info(request):
    return HttpResponse("live/info 응답")


def cam(request):
    if request.method == 'POST':
        image = request.FILES.get('camera-image')
        CameraImage.objects.create(image=image)
    images = CameraImage.objects.all()
    context = {
        'images': images
    }
    return render(request, 'cam.html', context)
