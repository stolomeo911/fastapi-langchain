from fastapi import FastAPI, Request, HTTPException, Response
from backend.pandasai_app.api.routes import agent, user
from backend.pandasai_app.api.utils.custom_json_encoder import CustomJSONResponse
from shared_libraries.utils import _fetch_secret_key
import logging
import json
import os

# get root logger
logger = logging.getLogger(__name__)

APOLLO_AUTHORIZED_TEAM_ID = _fetch_secret_key('APOLLO_AUTHORIZED_TEAM_ID', env=os.environ['ENV'])

app = FastAPI(default_response_class=CustomJSONResponse)


@app.middleware("http")
async def verify_slack_workspace(request: Request, call_next):
    try:
        body = await request.body()
        payload = json.loads(body.decode('utf-8'))
        team_id = payload.get("team_id")

        if team_id != APOLLO_AUTHORIZED_TEAM_ID:
            return Response(
                content=json.dumps({"status": 403, "detail": "Unauthorized workspace"}),
                status_code=403,
                media_type="application/json"
            )
    except Exception as e:
        logger.error(f"Error verifying Slack workspace: {e}")
        raise HTTPException(status_code=400, detail="Invalid request payload")

    response = await call_next(request)
    return response

app.include_router(agent.router, prefix='/agent')
app.include_router(user.router, prefix='/user')
