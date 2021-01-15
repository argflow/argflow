from typing import List
from os import path

import yaml

from starlette.responses import FileResponse
from starlette.routing import BaseRoute, Route
from starlette.schemas import BaseSchemaGenerator


def swagger_ui(req):
    return FileResponse(path.join(path.dirname(__file__), "swagger.html"), media_type="text/html")


class OpenAPI(BaseSchemaGenerator):
    def get_schema(self, routes: List[BaseRoute]) -> dict:
        with open(path.join(path.dirname(__file__), "api", "api.yaml")) as f:
            schema = yaml.safe_load(f)

        return schema

    def schema_route(self) -> Route:
        return Route(
            "/api/schema", endpoint=lambda req: self.OpenAPIResponse(req), include_in_schema=False
        )

    def swagger_ui_route(self):
        return Route("/api/docs", endpoint=swagger_ui, include_in_schema=False)
