from starlette.requests import Request
from starlette.responses import JSONResponse

from argflow_ui.api.router import router


@router.get("/chis")
def get_chis(req: Request):
    return JSONResponse(
        [
            {"name": "Hallucinations", "value": "hallucinations"},
            {"name": "Heatmaps", "value": "heatmaps"},
            {"name": "Identity", "value": "identity"},
        ]
    )
