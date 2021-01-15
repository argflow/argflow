import os

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .router import router


@router.get("/files")
def get_files(req: Request):
    path = req.query_params.get("path")

    if path is None:
        path = os.path.expanduser("~")

    path = os.path.abspath(path)

    if not os.path.exists(path) or not os.path.isdir(path):
        return Response(status_code=404)

    files, folders = get_files_and_folders(path)

    return JSONResponse({"path": path, "files": files, "folders": folders})


def get_files_and_folders(path):
    contents = os.listdir(path)
    files, folders = [], []

    for f in contents:
        if not f.startswith("."):
            f_path = os.path.join(path, f)
            if os.path.isdir(f_path):
                folders.append({"name": f, "path": f_path})
            else:
                files.append({"name": f, "path": f_path})

    return sorted(files, key=lambda n: str.casefold(n["name"])), sorted(
        folders, key=lambda n: str.casefold(n["name"])
    )
