import logging
import pickle

from aiortc import RTCSessionDescription, RTCPeerConnection, MediaStreamTrack
from aiortc.contrib.media import MediaBlackhole
from av.frame import Frame
from numpy.core.multiarray import ndarray
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

logger = logging.getLogger()

middleware = [
    # TODO: session per index load
]

peer_connections = set()


class FrameCaptureTrackWrapper(MediaStreamTrack):

    def __init__(self, track) -> None:
        self.track = track
        super().__init__()

    async def recv(self) -> Frame:
        """
        Receive the next frame.
        """
        frame = await self.track.recv()
        logger.info(f"{frame.time} - {frame.time_base} - {frame.key_frame}")
        array: ndarray = frame.to_ndarray()
        return frame


async def homepage(request):
    return JSONResponse({"hello": "world"})


async def rtc_session(request):
    params = await request.json()

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    peer_connection = RTCPeerConnection()

    recorder = MediaBlackhole()

    @peer_connection.on("track")
    def on_track(track):
        logger.info("Track Added!")

        @track.on("ended")
        async def on_ended():
            await recorder.stop()

        frame_capture = FrameCaptureTrackWrapper(track)

        recorder.addTrack(frame_capture)

    peer_connections.add(peer_connection)

    await peer_connection.setRemoteDescription(offer)
    await recorder.start()

    answer = await peer_connection.createAnswer()

    await peer_connection.setLocalDescription(answer)

    return JSONResponse({
        "sdp": peer_connection.localDescription.sdp,
        "type": peer_connection.localDescription.type
    })


routes = [
    Route("/home", endpoint=homepage),
    Route("/rtc", endpoint=rtc_session, methods=["POST"]),
    Mount("/", app=StaticFiles(directory="static", html=True), name="static"),
]

app = Starlette(debug=True, routes=routes, )
