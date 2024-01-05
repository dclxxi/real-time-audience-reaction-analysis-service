const recordButton = document.querySelector("#record-button");
const stopButton = document.querySelector("#stop-button");
const previewPlayer = document.querySelector("#preview");
const navButton = document.querySelectorAll("#nav-btn");

let recorder;
let recordedChunks;
let captureIntervalId;
let startTime;
let elapsedTimeIntervalId;
let time;
let elapsed_time = document.getElementById('elapsed-time');
let lecture_id = document.getElementById("id").dataset.id;
let term = parseInt(document.getElementById("term").dataset.term);
let flag = 0;
let isRecordingStopped = false;
let remainingDbSaves = 0;

function updateElapsedTime() {
    const elapsedTime = Date.now() - startTime;
    const hours = Math.floor(elapsedTime / 3600000);
    const minutes = Math.floor((elapsedTime % 3600000) / 60000);
    const seconds = Math.floor((elapsedTime % 60000) / 1000);
    elapsed_time.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function videoStart() {
    console.log('시작')
    flag = 1
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        previewPlayer.srcObject = stream;
        startRecording(previewPlayer.captureStream())
    })

    captureIntervalId = setInterval(recording, 60000 * term);
    startTime = Date.now();
    elapsedTimeIntervalId = setInterval(updateElapsedTime, 1000);

    time = 0;
}

function recording() {
    if (recorder && recorder.state === "recording") {
        recorder.stop();
    }

    recorder.onstop = async () => {
        const video = new Blob(recordedChunks, {type: "video/webm"});

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        context.drawImage(previewPlayer, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async (image) => {
            try {
                await sendFile(image, video);
            } catch (error) {
                console.error(error);
            }
        }, 'image/png');

        recordedChunks = [];
    }

    if (recorder && recorder.state === "inactive") {
        recorder.start();
    }

    time += term;
}


function startRecording(stream) {
    recordedChunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => {
        recordedChunks.push(e.data)
    }

    recorder.start();
}

function stopRecording() {
    alert('중지!')
    recorder.stop();
    previewPlayer.srcObject.getTracks().forEach(track => track.stop());

    clearInterval(captureIntervalId);
    clearInterval(elapsedTimeIntervalId);

    isRecordingStopped = true;
    sendTime(Date.now());
}

function cautionAlert(e) {
    if (flag === 1) {
        if (confirm("현재 반응 분석이 진행중입니다. 중단하시겠습니까?\n강의 내용은 저장되지 않습니다.")) {
        } else {
            e.preventDefault();
        }
    }
}

function sendTime(endTime) {
    const formData = new FormData();
    formData.append('lecture_id', lecture_id);
    formData.append('start_time', toTimeString(startTime));
    formData.append('end_time', toTimeString(endTime));

    $.ajax({
        url: '/live/time/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
            console.log('성공');
            $('#loading').show();
            $('body').css('overflow', 'hidden');
        },
        error: function (request, status, error) {
            console.log('에러');
            console.log(request);
            console.log(status);
            console.log(error);
        },
        complete: function () {
            console.log('완료');
            checkAndHideLoading();
        }
    })
}

function toTimeString(timestamp) {
    const date = new Date(timestamp);

    return date.toISOString().split('T')[1].split('.')[0];
}

function sendFile(image, video) {
    console.log('센드파일')
    const formData = new FormData();
    formData.append('lecture_id', lecture_id);
    formData.append('time', time);
    formData.append('image', image);
    formData.append('video', video);

    remainingDbSaves += 1;

    $.ajax({
        url: '/live/video/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
            console.log('성공');

            remainingDbSaves -= 1;
            checkAndHideLoading();

            const data = $.parseJSON(result);
            if ($.isEmptyObject(data)) {
                console.log('얼굴 인식 실패');
                return;
            }

            const emotion = $('#emotionImage');
            $('#reaction').empty();
            let audience_reaction = data['concentration'];
            $('#concentrationTextElement').text("집중도: " + audience_reaction + "%");
            if (audience_reaction >= 70) {
                console.log('긍정')
                emotion.attr("src", "/static/img/emotion/smile.png");
            } else if (audience_reaction >= 40) {
                console.log('중립')
                emotion.attr("src", "/static/img/emotion/neutral.png");
            } else {
                console.log('부정')
                emotion.attr("src", "/static/img/emotion/bad.png");
            }
        },
        error: function (request, status, error) {
            console.log('에러');
            console.log(request);
            console.log(status);
            console.log(error);
        }
    })
}

function checkAndHideLoading() {
    if (isRecordingStopped && (remainingDbSaves === 0)) {
        setTimeout(function () {
            // $('#loading').hide();
            $('body').css('overflow', 'auto');
            location.href = '/report/result/' + lecture_id + '/';
        }, 5000);
    }
}

recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
navButton.forEach((e) => {
    e.addEventListener('click', cautionAlert)
});
