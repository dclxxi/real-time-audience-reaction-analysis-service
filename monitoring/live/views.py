import os
from uuid import uuid4

from django.core.files.storage import default_storage
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
        uuid_name = uuid4().hex

        blob_name = f'{uuid_name}.jpg'
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return HttpResponse("image")


        uuid_name = uuid4().hex
        save_path = os.path.join(MEDIA_ROOT, uuid_name)

        img = img.convert('RGB')
        jpg_save_path = save_path + '.jpg'
        img.save(jpg_save_path, 'JPEG')

        return HttpResponse(jpg_save_path)


def lecture_list(request):
    lectures = Lecture.objects.all()
    context = {
        'lectures': lectures
    }

    return render(request, 'lecture_list.html', context)
