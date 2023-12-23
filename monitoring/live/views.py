import os
from uuid import uuid4

import moviepy.editor as mp
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from monitoring.settings import MEDIA_ROOT
from .models import CameraImage, Lecture

from google.cloud import storage
from google.oauth2 import service_account

import os.path

from google.cloud import speech

KEY_PATH = "C:/Users/user/Downloads/infra-earth-408904-fcc745c63739.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

client = storage.Client(credentials=credentials, project=credentials.project_id)


# Create your views here.
@csrf_exempt
def info(request):
    if request.method == "GET":
        return render(request, "info.html")

    if request.method == "POST":
        topic = request.POST.get("topic")
        term = request.POST.get("term")

        lecture = Lecture()
        lecture.topic = topic
        lecture.save()

        return redirect("live:record", id=lecture.id, term=term)

    return render(request, "cam.html")


@csrf_exempt
def cam(request):
    if request.method == "POST":
        image = request.FILES.get("camera-image")
        CameraImage.objects.create(image=image)
    images = CameraImage.objects.all()
    context = {"images": images}

    return render(request, "cam.html", context)


@csrf_exempt
def record(request, id, term):
    if request.method == "GET":
        return render(request, "record.html", context=dict(term=term))

    if request.method == "POST":
        pass


@csrf_exempt
def get_capture_file(request):
    if request.method == "POST" and "file" in request.FILES:
        file = request.FILES["file"]
        uuid_name = uuid4().hex

        blob_name = f"{uuid_name}.jpg"
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return HttpResponse("image")


@csrf_exempt
def get_video_file(request):
    if request.method == "POST" and "file" in request.FILES:
        file = request.FILES["file"]
        uuid_name = uuid4().hex

        blob_name = f"{uuid_name}.mp4"
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        mp3 = blob_path.split(".mp4")[0] + ".mp3"
        mp.ffmpeg_tools.ffmpeg_extract_audio(blob_path, mp3)

        bucket_name = "stt-test-bucket-aivle"
        upload_file_name = f"{uuid_name}.mp3"
        upload_file_path = mp3
        print("파일 이름", upload_file_path)

        bucket = client.get_bucket(bucket_name)
        mp3_blob = bucket.blob(upload_file_name)
        mp3_blob.upload_from_filename(upload_file_path)
        print(mp3_blob.public_url)

        run_stt(upload_file_name)

        if os.path.exists(blob_path):
            os.remove(blob_path)

        return HttpResponse("video")


def run_stt(upload_file_name):
    client = speech.SpeechClient()

    gcs_uri = f"gs://stt-test-bucket-aivle/{upload_file_name}"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        audio_channel_count=1,
        language_code="ko-KR",
    )

    # response = client.recognize(config=config, audio=audio)

    res = client.long_running_recognize(config=config, audio=audio)
    response = res.result()

    for result in response.results:
        print("script:{}".format(result.alternatives[0].transcript))


def lecture_list(request):
    lectures = Lecture.objects.all()
    context = {"lectures": lectures}

    return render(request, "lecture_list.html", context)
