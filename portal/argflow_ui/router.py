from typing import List

from starlette.routing import BaseRoute, Mount, Route


class Router:
    _routes: List[BaseRoute]

    def __init__(self) -> None:
        self._routes = []

    def add_route(self, route: BaseRoute):
        self._routes.append(route)

    def routes(self) -> List[BaseRoute]:
        return self._routes

    def route(self, path: str, methods: List[str] = ["GET"], include_in_schema: bool = True):
        def decorator(f):
            self.add_route(
                Route(path, endpoint=f, methods=methods, include_in_schema=include_in_schema)
            )
            return f

        return decorator

    def get(self, path: str, include_in_schema: bool = True):
        return self.route(path, methods=["GET"], include_in_schema=include_in_schema)

    def post(self, path: str, include_in_schema: bool = True):
        return self.route(path, methods=["POST"], include_in_schema=include_in_schema)

    def put(self, path: str, include_in_schema: bool = True):
        return self.route(path, methods=["PUT"], include_in_schema=include_in_schema)

    def delete(self, path: str, include_in_schema: bool = True):
        return self.route(path, methods=["DELETE"], include_in_schema=include_in_schema)

    def mount(self, path: str, router: "Router"):
        self._routes.append(Mount(path, routes=router.routes()))
