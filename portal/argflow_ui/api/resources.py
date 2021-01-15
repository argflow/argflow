import os.path
from pathlib import Path

from starlette.requests import Request
from starlette.responses import FileResponse, Response

from .router import router


@router.get("/resources/{path:path}")
def get_resource(req: Request):
    path = req.path_params["path"]
    path = os.path.realpath(os.path.join(req.app.resource_path, path))
    # Ensure that the path is actually referencing a file in the resource folder
    if not path.startswith(os.path.realpath(req.app.resource_path)):
        return Response(status_code=400)

    resource_file = Path(path)
    if not resource_file.is_file():
        return Response(status_code=404)

    return FileResponse(resource_file)
