import os
from uuid import uuid4

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from monitoring.settings import MEDIA_ROOT
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


@csrf_exempt
def get_capture_file(request):
    if request.method == "POST" and 'file' in request.FILES:
        file = request.FILES['file']
        print(file.name)

        uuid_name = uuid4().hex  # 이미지 이름이 한글, 공백이 섞여있기 때문에 uuid를 이용해서 이름을 바꿈
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        with open(save_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

    return HttpResponse(file)
