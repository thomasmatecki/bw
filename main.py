import logging

from aiortc import RTCSessionDescription, RTCPeerConnection
from aiortc.contrib.media import MediaBlackhole
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

logger = logging.getLogger()

middleware = [
    # TODO: session per index load
]

peer_connections = set()


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
        @track.on("ended")
        async def on_ended():
            await recorder.stop()

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
