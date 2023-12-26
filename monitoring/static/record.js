const recordButton = document.querySelector(".record-button");
const stopButton = document.querySelector(".stop-button");
const playButton = document.querySelector(".play-button");
const downloadButton = document.querySelector(".video-download-button");
const imgDownloadButton = document.querySelector(".img-download-button");
const captureButton = document.querySelector(".capture-button");
const previewPlayer = document.querySelector("#preview");
const recordingPlayer = document.querySelector("#recording");

let recorder;
let recordedChunks;
let captureIntervalId;
let startTime;
let elapsedTimeIntervalId;
let time;
let lecture_id = document.getElementById("id").dataset.id;
let term = parseInt(document.getElementById("term").dataset.term);


function updateElapsedTime() {
    const elapsedTime = Date.now() - startTime;
    const hours = Math.floor(elapsedTime / 3600000);
    const minutes = Math.floor((elapsedTime % 3600000) / 60000);
    const seconds = Math.floor((elapsedTime % 60000) / 1000);
    document.getElementById('elapsed-time').textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function videoStart() {
    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
        previewPlayer.srcObject = stream;
        startRecording(previewPlayer.captureStream())
    })

    captureIntervalId = setInterval(recording, 1000 * term);
    startTime = Date.now();
    elapsedTimeIntervalId = setInterval(updateElapsedTime, 1000);

    time = 0;
}

function recording() {
    recorder.stop();
    recorder.onstop = () => {
        const recordedBlob = new Blob(recordedChunks, {type: "video/webm"});
        sendVideoFile(recordedBlob).then(data => console.log(data)).catch(error => console.error(error));

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
    previewPlayer.srcObject.getTracks().forEach(track => track.stop());

    clearInterval(captureIntervalId);
}

function playRecording() {
    const recordedBlob = new Blob(recordedChunks, {type: "video/webm"});
    recordingPlayer.src = URL.createObjectURL(recordedBlob);
    recordingPlayer.play();
    downloadButton.href = recordingPlayer.src;
    downloadButton.download = `recording_${new Date()}.webm`;
    console.log(recordingPlayer.src);

    // sendVideoFile(recordedBlob).then(data => console.log(data)).catch(error => console.error(error));
}

function capture() {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    const img = document.getElementById('image');

    context.drawImage(previewPlayer, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        img.src = url;
        imgDownloadButton.href = url;
        imgDownloadButton.download = `capture_${new Date().toISOString()}.png`;

        sendImageFile(blob).then(data => console.log(data)).catch(error => console.error(error));
    }, 'image/png');
}

async function sendImageFile(file) {
    const formData = new FormData();
    formData.append('lecture_id', lecture_id);
    formData.append('time', time);
    formData.append('file', file);

    $.ajax({
        url: '/live/media/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
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

async function sendVideoFile(file) {
    const formData = new FormData();
    formData.append('lecture_id', lecture_id);
    formData.append('time', time);
    formData.append('file', file);

    $.ajax({
        url: '/live/video/',
        data: formData,
        method: 'POST',
        processData: false,
        contentType: false,
        success: function (result) {
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

recordButton.addEventListener("click", videoStart);
stopButton.addEventListener("click", stopRecording);
playButton.addEventListener("click", playRecording);
captureButton.addEventListener("click", recording);
