import os
from uuid import uuid4

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from monitoring.settings import MEDIA_ROOT
from .models import CameraImage, Lecture


# Create your views here.
@csrf_exempt
def info(request):
    if request.method == 'GET':
        return render(request, 'info.html')

    if request.method == 'POST':
        topic = request.POST.get('topic')
        term = request.POST.get('term')

        lecture = Lecture()
        lecture.topic = topic
        lecture.save()

        return redirect("live:record", id=lecture.id, term=term)

    return render(request, 'cam.html')


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
def record(request, id, term):
    if request.method == 'GET':
        return render(request, 'record.html', context=dict(term=term))

    if request.method == 'POST':
        pass


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
