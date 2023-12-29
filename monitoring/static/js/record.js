const recordButton = document.querySelector("#record-button");
const stopButton = document.querySelector("#stop-button");
const previewPlayer = document.querySelector("#preview");

let recorder;
let recordedChunks;
let captureIntervalId;
let startTime;
let elapsedTimeIntervalId;
let time;
let elapsed_time = document.getElementById('elapsed-time');
let lecture_id = document.getElementById("id").dataset.id;
let term = parseInt(document.getElementById("term").dataset.term);


function updateElapsedTime() {
    const elapsedTime = Date.now() - startTime;
    const hours = Math.floor(elapsedTime / 3600000);
    const minutes = Math.floor((elapsedTime % 3600000) / 60000);
    const seconds = Math.floor((elapsedTime % 60000) / 1000);
    elapsed_time.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function videoStart() {
    console.log('시작')
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
    recorder.stop();
    recorder.onstop = () => {
        const video = new Blob(recordedChunks, {type: "video/webm"});

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        context.drawImage(previewPlayer, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async (image) => {
            await sendFile(image, video).catch(error => console.error(error));
        }, 'image/png');

        recordedChunks = [];
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
    previewPlayer.srcObject.getTracks().forEach(track => track.stop());

    clearInterval(captureIntervalId);
    clearInterval(elapsedTimeIntervalId);

    sendTime(Date.now()).catch(error => console.error(error));
}

async function sendTime(endTime, elapsedTime) {
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
            location.href = '/report/result/' + lecture_id + '/';
            console.log('성공');
        },
        error: function (request, status, error) {
            console.log('에러');
            console.log(request);
            console.log(status);
            console.log(error);
        }
    })
}

function toTimeString(timestamp) {
    const date = new Date(timestamp);

    return date.toISOString().split('T')[1].split('.')[0];
}

async function sendFile(image, video) {
    console.log('센드파일')
    const formData = new FormData();
    formData.append('lecture_id', lecture_id);
    formData.append('time', time);
    formData.append('image', image);
    formData.append('video', video);

    $.ajax({
        url: '/live/video/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
            console.log('성공');
            const data = $.parseJSON(result);
            $('#reaction').empty()
            $(data).each(function (i, val) {
                $.each(val, function (k, v) {
                    console.log(k + " : " + v);
                    $('#reaction').append('<p>' + k + ' : ' + v + '</p>');
                });
            });
        },
        error: function (request, status, error) {
            console.log('에러');
            console.log(request);
            console.log(status);
            console.log(error);
        }
    })
}

recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
