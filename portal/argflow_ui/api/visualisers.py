from starlette.requests import Request
from starlette.responses import JSONResponse

from .router import router


@router.get("/visualisers")
def get_visualisers(req: Request):
    results = []

    for v in req.app.visualisers.values():
        results.append(
            {
                "name": v.get_name(),
                "id": v.get_identifier(),
                "main": "/modules/" + v.get_identifier(),
            }
        )

    return JSONResponse(results)
