import asyncio
import os
import shutil
import requests
import zipfile

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from argflow_ui.api.utils import folder_size
from argflow_ui.api.data import cached_explanations, MODEL_DIRNAME
from argflow_ui.api.router import router


@router.get("/models")
def get_models(req: Request):
    results = []

    for name in os.listdir(req.app.resource_path):
        path = os.path.join(req.app.resource_path, name)
        model_path = os.path.join(path, MODEL_DIRNAME)

        if os.path.isdir(model_path):
            results.append(
                {"name": name, "size": folder_size(path), "path": path, "url": f"/models/{name}"}
            )

    return JSONResponse(sorted(results, key=lambda x: x["name"]))


def import_model(location, model, target):
    if location == "fs":
        os.makedirs(target)
        tmp_dir = os.path.join(target, f"_{MODEL_DIRNAME}")
        final_dir = os.path.join(target, MODEL_DIRNAME)
        shutil.copytree(model, tmp_dir)
        os.rename(tmp_dir, final_dir)

    elif location == "hub":
        res = requests.get(model)

        if res.status_code != 200:
            return

        os.makedirs(target)
        path = os.path.join(target, "model.zip")

        with open(path, "wb") as f:
            f.write(res.content)

        with zipfile.ZipFile(path) as zip:
            zip.extractall(os.path.join(target))


@router.post("/models/{model_name}")
async def create_model(req: Request):
    hub_url = req.app.hub_url
    model_name: str = req.path_params["model_name"]
    body = await req.json()

    location = body["location"]
    model = body["model"]

    if location == "hub":
        if not hub_url:
            return Response(status_code=501)
        model = f"{hub_url}/api/model/{model}/download"

    path = os.path.join(req.app.resource_path, model_name)

    if os.path.exists(path):
        return Response(status_code=400)

    # Import the model in a subprocess
    asyncio.get_event_loop().run_in_executor(req.app.executor, import_model, location, model, path)

    return Response(status_code=200)


@router.delete("/models/{model_name}")
def delete_model(req: Request):
    model_name: str = req.path_params["model_name"]
    model_path = os.path.join(req.app.resource_path, model_name)

    # Ensure that the path is actually referencing a directory in the resource folder
    if not model_path.startswith(os.path.realpath(req.app.resource_path)):
        return Response(status_code=400)

    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
    else:
        return Response(status_code=404)

    if model_name in cached_explanations:
        del cached_explanations[model_name]

    return Response(status_code=204)
