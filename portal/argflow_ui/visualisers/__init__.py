from abc import ABC, abstractmethod
from os import path
from starlette.responses import JSONResponse, Response
from .argumentation_views import (
    ArgumentationGraphView,
    GraphArgumentationGraphView,
    ConversationArgumentationGraphView,
)


class VisualiserResponse:
    def serialize(self):
        return Response(status_code=501)


class VisualiserErrorResponse(VisualiserResponse):
    def __init__(self, status_code=501):
        self.status_code = status_code

    def serialize(self):
        return Response(status_code=self.status_code)


class VisualiserExplanationResponse(VisualiserResponse):
    def __init__(self, data):
        self.data = data

    def serialize(self):
        return JSONResponse(self.data)


class Visualiser(ABC):
    def __init__(self):
        self.session = None

    def get_name(self):
        return self.__class__.__qualname__

    def get_identifier(self):
        return self.__class__.__module__ + "." + self.__class__.__qualname__

    @abstractmethod
    def get_module_path(self):
        pass

    def create_session(self, graph):
        self.session = VisualiserSession(self, ArgumentationGraphView(graph))
        return self.session

    def destroy_session(self):
        self.session = None

    def process_explanation_request(self, data):
        if self.session is None:
            return VisualiserErrorResponse(status_code=404)
        return self.session.process_explanation_request(data)


class VisualiserSession:
    def __init__(self, visualiser, view):
        self.visualiser = visualiser
        self.view = view

    async def on_connect(self, websocket):
        pass

    async def on_receive(self, websocket, data):
        pass

    async def on_disconnect(self, websocket, close_code):
        pass

    def process_explanation_request(self, data):
        return VisualiserExplanationResponse(self.view.serialize())


class GraphVisualiser(Visualiser):
    def get_name(self):
        return "Graph"

    def get_module_path(self):
        return path.join(path.dirname(__file__), "js/argflow-ui-graph.js")

    def create_session(self, graph):
        self.session = GraphVisualiserSession(self, GraphArgumentationGraphView(graph))
        return self.session


class GraphVisualiserSession(VisualiserSession):
    def process_explanation_request(self, data):
        if data.get("prune"):
            kwargs = dict(limit=data.get("limit"), layer_limit=data.get("layer_limit"))

            # Use default argument if limit or layer_limit is not provided
            self.view.prune_graph(**{k: v for k, v in kwargs.items() if v is not None})

        return VisualiserExplanationResponse(self.view.serialize())


class ConversationVisualiser(Visualiser):
    def get_name(self):
        return "Conversation"

    def get_module_path(self):
        return path.join(path.dirname(__file__), "js/argflow-ui-conversation.js")

    def create_session(self, graph):
        self.session = ConversationVisualiserSession(
            self, ConversationArgumentationGraphView(graph)
        )
        return self.session


class ConversationVisualiserSession(VisualiserSession):
    def process_explanation_request(self, data):
        if data.get("reset") == "true":
            primary_node = req.query_params.get("primary_node")
            secondary_nodes = req.query_params.get("secondary_nodes") or []
            try:
                self.view.set_state(primary=primary_node, secondary=secondary_nodes)
            except ValueError:
                return VisualiserErrorResponse(status_code=400)

        # Perform interaction specified in the request if there is any
        interaction_target = data.get("interaction_target")
        interaction_direction = data.get("interaction_direction")
        interaction_result = None
        if interaction_target is not None and interaction_direction is not None:
            contribution_type = data.get("contribution_type")
            limit = data.get("limit")

            interaction_target = interaction_target
            limit = int(limit) if limit is not None else None

            try:
                self.view.perform_interaction(
                    interaction_target, interaction_direction, contribution_type, limit
                )
            except ValueError:
                return VisualiserErrorResponse(status_code=400)

        return VisualiserExplanationResponse(self.view.serialize())
