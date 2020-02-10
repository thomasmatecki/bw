const recordedChunks = [];

$(function() {

    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = function() {
        ws.send("Connection established. Hello server!");
    };

    ws.onmessage = function(msg) {
        console.log(msg);
    };

    navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {
            facingMode: ["user", "environment"]
        }
    }).then(mediaStream => {
        let vidEl = $('video');

        vidEl[0].srcObject = mediaStream;

        const options = {
            mimeType: 'video/webm'
        };

        const mediaRecorder = new MediaRecorder(mediaStream, options);

        mediaRecorder.ondataavailable = function(e) {
            ws.send(e.data);
        };

        mediaRecorder.start();

        $("#stop").click(function() {
            mediaRecorder.stop();
        });
    }); //.catch( error => {})
});
