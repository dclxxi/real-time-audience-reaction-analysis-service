import json
import os
import os.path
from uuid import uuid4

import cv2
import moviepy.editor as mp
import numpy as np
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from google.cloud import speech
from google.cloud import storage
from google.oauth2 import service_account
from matplotlib import pyplot as plt
from openai import OpenAI
from tensorflow.keras.models import load_model

from monitoring.settings import MEDIA_ROOT
from report.models import Feedback, Reaction
from user.models import User
from .models import Lecture

KEY_PATH = "C:/Users/user/Downloads/infra-earth-408904-fcc745c63739.json"
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

client = storage.Client(credentials=credentials, project=credentials.project_id)

openai = OpenAI(api_key="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")  # 본인 API키로 수정해서 실행해주세요


# Create your views here.
@csrf_exempt
@login_required
def info(request):
    if request.method == "GET":
        return render(request, "info.html")

    if request.method == "POST":
        topic = request.POST.get("topic")
        term = request.POST.get("term")

        lecture = Lecture()
        lecture.topic = topic
        lecture.user = get_object_or_404(User, pk=request.user.pk)
        lecture.save()

        request.session['lecture_id'] = lecture.id

        return redirect("live:record", id=lecture.id, term=term)


@csrf_exempt
@login_required
def record(request, id, term):
    session_lecture_id = request.session.get('lecture_id')

    if not session_lecture_id or session_lecture_id != id:
        return redirect("live:info")

    if request.method == "GET":
        return render(request, "record.html", context=dict(id=id, term=term))

    if request.method == "POST":
        pass


@csrf_exempt
def get_capture_file(request):
    if request.method == "POST" and "image" in request.FILES:
        lecture_id = request.POST.get('lecture_id')
        time = request.POST.get('time')
        image = request.FILES["image"]

        uuid_name = uuid4().hex

        blob_name = f"{uuid_name}.jpg"
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # mlflow

        lecture = get_object_or_404(Lecture, pk=lecture_id)

        reaction = Reaction()
        reaction.lecture = lecture
        reaction.time = time
        reaction.concentration = 0
        reaction.negative = 0
        reaction.neutral = 0
        reaction.positive = 0
        reaction.save()

        return HttpResponse("image")


@csrf_exempt
def get_video_file(request):
    if request.method == "POST" and "video" in request.FILES and "image" in request.FILES:
        lecture_id = request.POST.get('lecture_id')
        time = request.POST.get('time')
        image = request.FILES["image"]
        video = request.FILES["video"]

        uuid_name = uuid4().hex

        blob_name = f"{uuid_name}.jpg"
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        results = model(blob_path)

        if sum(results.values()) == 0:
            return HttpResponse(status=200)

        lecture = get_object_or_404(Lecture, pk=lecture_id)

        reaction = Reaction()
        reaction.lecture = lecture
        reaction.time = time
        reaction.concentration = results.get('concentration')
        reaction.negative = results.get('negative')
        reaction.neutral = results.get('neutral')
        reaction.positive = results.get('positive')
        reaction.save()

        blob_name = f"{uuid_name}.mp4"
        blob_path = os.path.join(MEDIA_ROOT, blob_name)
        with default_storage.open(blob_path, "wb+") as destination:
            for chunk in video.chunks():
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

        audio_content = run_stt(upload_file_name)
        print('출력: ', audio_content)

        # feedback_content = chatGPT(lecture.topic, audio_content)
        feedback_content = f"{lecture.topic} 주제의 피드백입니다."

        feedback = Feedback()
        feedback.reaction = reaction
        feedback.content = feedback_content
        feedback.save()

        return HttpResponse(json.dumps(results))


def model(blob_path):
    def load_detection_model(model_path):
        detection_model = cv2.CascadeClassifier(model_path)
        return detection_model

    def detect_faces(detection_model, gray_image_array):
        return detection_model.detectMultiScale(gray_image_array, 1.3, 5)

    def draw_bounding_box(face_coordinates, image_array, color):
        x, y, w, h = face_coordinates
        cv2.rectangle(image_array, (x, y), (x + w, y + h), color, 2)

    def apply_offsets(face_coordinates, offsets):
        x, y, width, height = face_coordinates
        x_off, y_off = offsets
        return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)

    def draw_text(coordinates, image_array, text, color, x_offset=0, y_offset=0, font_scale=0.5, thickness=2):
        x, y = coordinates[:2]
        cv2.putText(image_array, text, (x + x_offset, y + y_offset), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color,
                    thickness, cv2.LINE_AA)

    def preprocess_input(x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x

    image_path = blob_path
    detection_model_path = 'haarcascade_frontalface_default.xml'
    emotion_model_path = 'emotion_temp.h5'
    emotion_labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'sad', 5: 'surprise', 6: 'neutral'}
    font = cv2.FONT_HERSHEY_SIMPLEX
    emotion_offsets = (0, 0)
    face_detection = load_detection_model(detection_model_path)
    emotion_classifier = load_model(emotion_model_path, compile=False)
    emotion_target_size = emotion_classifier.input_shape[1:3]
    rgb_image = cv2.imread(image_path)
    gray_image = cv2.imread(image_path, 0)

    def highest_emotion(positive, neutral, negative):
        if positive == max([positive, neutral, negative]):
            return 'positive'
        elif neutral == max([positive, neutral, negative]):
            return 'neutral'
        else:
            return 'negative'

    def engagement_score(scores):
        if ((scores[6] > 0.6) | (scores[3] > 0.5) | (scores[5] > 0.6) | (scores[0] > 0.2) | (scores[1] > 0.2) | (
                scores[2] > 0.3) | (scores[4] > 0.3)):
            return ((scores[0] * 0.2) + (scores[1] * 0.2) + (scores[2] * 0.3) + (scores[3] * 0.7) + (
                    scores[4] * 0.3) + (scores[5] * 0.7) + (scores[6] * 1.0))
        else:
            return 0

    positives = []
    neutrals = []
    negatives = []
    engagements = []
    faces = detect_faces(face_detection, rgb_image)
    for face_coordinates in faces:
        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        gray_face = cv2.resize(gray_face, (emotion_target_size))

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)

        emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
        engagement = engagement_score(emotion_classifier.predict(gray_face)[0])
        positive = emotion_classifier.predict(gray_face)[0][3] + emotion_classifier.predict(gray_face)[0][5]
        neutral = emotion_classifier.predict(gray_face)[0][6]
        negative = emotion_classifier.predict(gray_face)[0][0] + emotion_classifier.predict(gray_face)[0][1] + \
                   emotion_classifier.predict(gray_face)[0][2] + emotion_classifier.predict(gray_face)[0][4]
        positives.append(positive)
        neutrals.append(neutral)
        negatives.append(negative)
        engagements.append(engagement)
        emotion_text = highest_emotion(positive, neutral, negative)
        color = (0, 255, 255)

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_text, color, -20, -20, 0.7, 2)
    plt.imshow(rgb_image)
    cv2.imwrite('result_emotion_image.jpg', rgb_image)

    def calculate_percentage(emotion):
        if len(emotion) == 0:
            return 0
        else:
            return int(round(sum(emotion) / len(emotion), 2) * 100)

    positive = calculate_percentage(positives)
    neutral = calculate_percentage(neutrals)
    negative = calculate_percentage(negatives)
    concentration = calculate_percentage(engagements)
    results = {
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "concentration": concentration,
    }
    return results


def calculate_percentage(emotion):
    if len(emotion) == 0:
        return 0
    else:
        return int(round(sum(emotion) / len(emotion), 2) * 100)


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
                                                                                  "제공해야 합니다. 강점, 약점, 개선 방법을 순서대로 작성해주세요."},
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
