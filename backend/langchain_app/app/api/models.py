from pydantic import BaseModel
from typing import List


class Dataset(BaseModel):
    metadata: dict
    session_id: str


class SuggestedQuestionsResponse(BaseModel):
    questions: List[str]


class Message(BaseModel):
    user_input: str
    session_id: str
    user_id: str


# Define the Response model
class ModelResponse(BaseModel):
    user_input: str
    response: str