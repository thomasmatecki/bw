const recordedChunks = [];

$(function () {

    const config = {
        // https://www.callstats.io/blog/what-is-unified-plan-and-how-will-it-affect-your-webrtc-development
        sdpSemantics: 'unified-plan'
    };


    const peerConnection = new RTCPeerConnection(config);

    const constraints = {
        audio: false,
        video: {
            facingMode: ["user", "environment"]
        }
    };

    function negotiate() {
        return peerConnection.createOffer().then(
            offer => peerConnection.setLocalDescription(offer)
        ).then(
            () => new Promise(resolve => {
                // wait for ICE gathering to complete
                if (peerConnection.iceGatheringState === 'complete') {
                    resolve();
                } else {
                    function checkState() {
                        if (peerConnection.iceGatheringState === 'complete') {
                            peerConnection.removeEventListener('icegatheringstatechange', checkState);
                            resolve();
                        }
                    }

                    peerConnection.addEventListener('icegatheringstatechange', checkState);
                }
            })
        ).then(function () {
            const offer = peerConnection.localDescription;

            return fetch('/rtc', {
                body: JSON.stringify({
                    sdp: offer.sdp,
                    type: offer.type,
                }),
                headers: {
                    'Content-Type': 'application/json'
                },
                method: 'POST'
            });
        }).then(function (response) {
            return response.json();
        }).then(function (answer) {
            return peerConnection.setRemoteDescription(answer);
        }).catch(function (e) {
            alert(e);
        });
    }

    navigator.mediaDevices.getUserMedia(constraints).then(
        mediaStream => {

            let vidEl = $('video');

            vidEl[0].srcObject = mediaStream;

            mediaStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, mediaStream);
            });

            return negotiate();
        },
        error => {
            alert('Could not acquire media: ' + error);
        }); //.catch( error => {})
})
;
