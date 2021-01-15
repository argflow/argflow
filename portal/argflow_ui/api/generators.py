from starlette.requests import Request
from starlette.responses import JSONResponse

from .router import router


@router.get("/generators")
def get_generators(req: Request):
    results = []

    for v in req.app.generators.keys():
        results.append(v)

    return JSONResponse(results)
