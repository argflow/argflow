import json
import os
import shutil
import asyncio

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from argflow_ui.argumentation_graph import ArgumentationGraph
from argflow_ui.api.utils import folder_size
from argflow_ui.api.router import router
from argflow_ui.api.data import GRAPH_FILENAME, cached_explanations


@router.get("/models/{model_name}/explanations")
def get_explanations(req: Request):
    model_name: str = req.path_params["model_name"]
    model_path = os.path.join(req.app.resource_path, model_name)
    results = []

    if not os.path.isdir(model_path):
        return Response(status_code=404)

    for name in os.listdir(model_path):
        explanation_path = os.path.join(model_path, name)
        graph_path = os.path.join(explanation_path, GRAPH_FILENAME)

        if os.path.isdir(explanation_path) and os.path.isfile(graph_path):
            results.append(
                {
                    "name": name,
                    "path": explanation_path,
                    "size": folder_size(explanation_path),
                    "url": f"/models/{model_name}/explanations/{name}",
                }
            )

    return JSONResponse(sorted(results, key=lambda x: x["name"]))


def run_generator(generator, resource_path, model_name, model_input, explanation_name, chi_value):
    import importlib.util

    module_path, class_name = generator
    spec = importlib.util.spec_from_file_location("generator", module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    generator = getattr(mod, class_name)()

    generator.generate(resource_path, model_name, model_input, explanation_name, chi_value)


@router.post("/models/{model_name}/explanations/{explanation_name}")
async def create_explanation(req: Request):
    model_name: str = req.path_params["model_name"]
    explanation_name: str = req.path_params["explanation_name"]
    body = await req.json()

    input_text = body["input"]
    chi_value = body["chi"]
    generator_name = body["generator"]

    output_path = os.path.join(req.app.resource_path, model_name, explanation_name)

    if os.path.exists(output_path):
        return Response(status_code=400)

    generator = req.app.generators[generator_name]
    resource_path = req.app.resource_path

    async def task():
        for ws in req.app.ws_clients:
            await ws.send_json({"type": "exgen-start"})

        # Run the explanation generator in a subprocess
        await asyncio.get_event_loop().run_in_executor(
            req.app.executor,
            run_generator,
            generator,
            resource_path,
            model_name,
            input_text,
            explanation_name,
            chi_value,
        )

        for ws in req.app.ws_clients:
            await ws.send_json({"type": "exgen-success", "name": explanation_name})

    asyncio.create_task(task())

    return Response(status_code=200)


@router.get("/models/{model_name}/explanations/{explanation_name}")
def get_explanation(req: Request):
    model_name: str = req.path_params["model_name"]
    explanation_name: str = req.path_params["explanation_name"]

    if (
        model_name not in cached_explanations
        or explanation_name not in cached_explanations[model_name]
    ):
        graph_path = os.path.join(
            req.app.resource_path, model_name, explanation_name, GRAPH_FILENAME
        )

        try:
            with open(graph_path, "r") as f:
                content = f.read()
                explanation = json.loads(content)
        except OSError:
            return Response(status_code=404)

        try:
            if model_name not in cached_explanations:
                cached_explanations[model_name] = {}

            arg_graph = ArgumentationGraph(explanation)
        except ValueError as e:
            return Response(status_code=400)

        cached_explanations[model_name][explanation_name] = arg_graph

    explanation = cached_explanations[model_name][explanation_name]

    return JSONResponse(explanation)


@router.post("/models/{model_name}/explanations/{explanation_name}/visualisers/{visualiser_id}")
async def fetch_explanation(req: Request):
    model_name: str = req.path_params["model_name"]
    explanation_name: str = req.path_params["explanation_name"]
    visualiser_id: str = req.path_params["visualiser_id"]
    visualiser_data: str = await req.json()

    if visualiser_id not in req.app.visualisers:
        return Response(status_code=404)

    visualiser = req.app.visualisers[visualiser_id]

    return visualiser.process_explanation_request(visualiser_data).serialize()


@router.delete("/models/{model_name}/explanations/{explanation_name}")
def delete_explanation(req: Request):
    model_name: str = req.path_params["model_name"]
    explanation_name: str = req.path_params["explanation_name"]
    explanation_path = os.path.join(req.app.resource_path, model_name, explanation_name)

    # Ensure that the path is actually referencing a directory in the resource folder
    if not explanation_path.startswith(os.path.realpath(req.app.resource_path)):
        return Response(status_code=400)

    if os.path.isdir(explanation_path):
        shutil.rmtree(explanation_path)
    else:
        return Response(status_code=404)

    if model_name in cached_explanations and explanation_name in cached_explanations[model_name]:
        del cached_explanations[model_name][explanation_name]

    return Response(status_code=204)
