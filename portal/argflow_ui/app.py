import json
import os.path
import uvicorn

from concurrent.futures import ProcessPoolExecutor

from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, PlainTextResponse, Response
from starlette.routing import WebSocketRoute
from starlette.websockets import WebSocket

from argflow.portal import ExplanationGenerator

from argflow_ui.api import router as api
from argflow_ui.api.explanations import GRAPH_FILENAME
from argflow_ui.argumentation_graph import ArgumentationGraph
from argflow_ui.openapi import OpenAPI
from argflow_ui.router import Router
from argflow_ui.visualisers import Visualiser
from argflow_ui.watcher import FileWatcher


class MainWSEndpoint(WebSocketEndpoint):
    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        websocket.app.ws_clients.append(websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        websocket.app.ws_clients.remove(websocket)


class VSessionWSEndpoint(WebSocketEndpoint):
    """
    Websocket endpoint for visualiser sessions.
    """

    encoding = "json"

    async def on_connect(self, websocket: WebSocket) -> None:
        app = websocket.app

        visualiser_id = websocket.query_params["visualiser"]
        model_name = websocket.query_params["model"]
        explanation_name = websocket.query_params["explanation"]

        visualiser = app.visualisers[visualiser_id]
        path = os.path.join(app.resource_path, model_name, explanation_name, GRAPH_FILENAME)

        try:
            with open(path, "r") as f:
                content = f.read()
                explanation = json.loads(content)
        except OSError:
            return Response(status_code=404)

        try:
            graph = ArgumentationGraph(explanation)
        except ValueError:
            return Response(status_code=400)

        await websocket.accept()

        self.session = visualiser.create_session(graph)

        await self.session.on_connect(websocket)

    async def on_receive(self, websocket: WebSocket, data) -> None:
        await self.session.on_receive(websocket, data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        self.session.visualiser.destroy_session()
        await self.session.on_disconnect(websocket, close_code)


class ArgflowUI(Starlette):
    def __init__(self, resource_path=None, client_path=None, hub_url=None):
        self.resource_path = resource_path if resource_path is not None else os.path.abspath(".")
        self.package_path = os.path.abspath(os.path.dirname(__file__))
        self.client_path = (
            client_path if client_path is not None else os.path.join(self.package_path, "client")
        )

        self.hub_url = hub_url

        self.generators = {}
        self.visualisers = {}
        self.modules = {}
        self.ws_clients = []

        async def on_file_watcher_event(changes):
            for socket in self.ws_clients:
                await socket.send_json({"type": "reload"})

        self.watcher = FileWatcher(self.resource_path, on_event=on_file_watcher_event)
        self.executor = ProcessPoolExecutor()

        default_generator = os.path.join(os.path.dirname(__file__), "generator/default.py")
        self.add_explanation_generator(
            default_generator, "DefaultExplanationGenerator", name="default"
        )

        openapi = OpenAPI()
        router = Router()

        router.add_route(openapi.schema_route())
        router.add_route(openapi.swagger_ui_route())

        router.mount("/api", api)

        router.add_route(WebSocketRoute("/ws", endpoint=MainWSEndpoint))
        router.add_route(WebSocketRoute("/ws/session", endpoint=VSessionWSEndpoint))

        @router.get("/modules/{path:path}")
        def get_js_module(req: Request):
            path = req.path_params["path"]
            module = self.modules.get(path)

            if module is None:
                return Response(status_code=404)

            return FileResponse(module)

        @router.get("/{path:path}")
        def fallback(req: Request):
            if not os.path.isdir(self.client_path):
                return PlainTextResponse(
                    "Client static files not found. If you are a developer of ArgFlow, make sure "
                    "to run `poetry run task build-frontend` to be able to serve the frontend. If "
                    "you are a user of ArgFlow, please contact the developers."
                )

            path: str = os.path.normpath(req.path_params["path"])
            path = os.path.join(self.client_path, path)

            if not os.path.isfile(path):
                path = os.path.join(self.client_path, "index.html")

            return FileResponse(path)

        super().__init__(
            debug=True,
            routes=router.routes(),
            on_startup=[lambda: self.watcher.start()],
        )

    def register_visualiser(self, visualiser: Visualiser):
        self.register_js_module(visualiser.get_identifier(), visualiser.get_module_path())
        self.visualisers[visualiser.get_identifier()] = visualiser

    def register_js_module(self, name: str, path: str):
        if name in self.modules:
            raise RuntimeError(f"A module named '{name}' has already been registered'")

        if not os.path.isfile(path):
            raise RuntimeError(f"{path} is not a file")

        self.modules[name] = path

    def add_explanation_generator(self, module_path: str, class_name: str, name: str = None):
        if not name:
            name = class_name

        self.generators[name] = (module_path, class_name)

    def set_explanation_generator(self, generator: ExplanationGenerator):
        self._explanation_generator = generator

    def run(self, launch_browser=True):
        print("--------------------------------------------")

        print("Resource Directory: " + self.resource_path)
        print("Client Root: " + self.client_path)

        if len(self.visualisers) > 0:
            print("Visualisers:")

            for name, v in self.visualisers.items():
                print(f"  - {name}")

        if len(self.modules) > 0:
            print("Loaded modules:")

            for name, path in self.modules.items():
                print(f"  - {name} -> {path}")

        print("--------------------------------------------")

        if launch_browser:
            import webbrowser

            webbrowser.open("http://localhost:8000")

        uvicorn.run(self)
