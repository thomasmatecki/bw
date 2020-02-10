import logging
from random import randint
from time import time

from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

logger = logging.getLogger()


middleware = [
    # TODO: session per index load
]

async def homepage(request):
    return JSONResponse({"hello": "world"})


class Echo(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        await websocket.send_text("Hello, websocket!")

    async def on_receive(self, websocket: WebSocket, data):
        logger.info(f"data received: {len(data)}")

        if isinstance(data, str):
            return

        with open(f"media/segment-{time()}", "wb") as out_file:
            out_file.write(data)


routes = [
    Route("/home", endpoint=homepage),
    WebSocketRoute("/ws", Echo),
    Mount("/", app=StaticFiles(directory="static", html=True), name="static"),
]

app = Starlette(debug=True, routes=routes, )
