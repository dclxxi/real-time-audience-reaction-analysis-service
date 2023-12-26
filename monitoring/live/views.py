import os
import os.path
from uuid import uuid4

import moviepy.editor as mp
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from google.cloud import speech
from google.cloud import storage
from google.oauth2 import service_account
from openai import OpenAI

from monitoring.settings import MEDIA_ROOT
from report.models import Feedback
from .models import CameraImage, Lecture

KEY_PATH = "C:/Users/user/Downloads/infra-earth-408904-fcc745c63739.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

client = storage.Client(credentials=credentials, project=credentials.project_id)

openai = OpenAI(api_key="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")  # 본인 API키로 수정해서 실행해주세요


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
        return render(request, "record.html", context=dict(id=id, term=term))

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
        lecture_id = request.POST.get('lecture_id')
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

        bucket = client.get_bucket(bucket_name)
        mp3_blob = bucket.blob(upload_file_name)
        mp3_blob.upload_from_filename(upload_file_path)
        print(mp3_blob.public_url)

        lecture = get_object_or_404(Lecture, pk=lecture_id)

        audio_content = run_stt(upload_file_name)
        feedback_content = chatGPT(lecture.topic, audio_content)

        feedback = Feedback()
        feedback.lecture = lecture
        feedback.content = feedback_content
        feedback.save()

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

    audio_content = ''
    for result in response.results:
        audio_content += result.alternatives[0].transcript

    return audio_content


def chatGPT(topic, prompt):
    content = f"강의 주제: {topic}\n강의 내용: {prompt}"
    completion = openai.chat.completions.create(model="gpt-3.5-turbo",
                                                messages=[
                                                    {"role": "system", "content": "당신은 교육 전문가로서, 강의 내용에 대한 피드백을 "
                                                                                  "제공해야 합니다. 강점, 약점, 개선 방법을 작성해주세요."},
                                                    {"role": "user", "content": content}
                                                ])
    print(completion)
    result = completion.choices[0].message.content

    return result


def imageGPT(prompt):
    response = openai.images.generate(prompt=prompt,
                                      n=1,
                                      size="256x256")
    result = response['data'][0]['url']

    return result


def lecture_list(request):
    lectures = Lecture.objects.all()
    context = {"lectures": lectures}

    return render(request, "lecture_list.html", context)
