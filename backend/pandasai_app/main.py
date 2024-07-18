from fastapi import FastAPI, Request, HTTPException, Response
from backend.pandasai_app.api.routes import agent, user
from backend.pandasai_app.api.utils.custom_json_encoder import CustomJSONResponse
from shared_libraries.utils import _fetch_secret_key
import logging
import json
import os

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI(default_response_class=CustomJSONResponse)

app.include_router(agent.router, prefix='/agent')
app.include_router(user.router, prefix='/user')
