import io
import os.path

from google.cloud import speech


def run_stt():
    client = speech.SpeechClient()

    gcs_uri = "gs://stt-test-bucket-aivle/test.mp3"

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


if __name__ == "__main__":
    run_stt()
