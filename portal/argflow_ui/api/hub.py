import requests

from starlette.requests import Request
from starlette.responses import JSONResponse, Response


from .router import router


@router.get("/hub/enabled")
def is_enabled(req: Request):
    return JSONResponse(True if req.app.hub_url else False)


@router.get("/hub/models/search")
def search_models(req: Request):
    hub_url = req.app.hub_url

    if not hub_url:
        return Response(status_code=501)

    query = req.query_params["query"]
    res = requests.get(f"{hub_url}/api/model/search/{query}")
    data = res.json()

    return JSONResponse(data)
