import json
import numpy as np
from fastapi.responses import JSONResponse


def custom_json_encoder(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError


class CustomJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return json.dumps(content, default=custom_json_encoder).encode("utf-8")