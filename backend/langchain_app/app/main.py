import uvicorn
from fastapi import FastAPI
from .api.routes import agent


app = FastAPI()


@app.get("/")
async def root():
    return {"status": "OK"}


app.include_router(agent.router, prefix='/agent')