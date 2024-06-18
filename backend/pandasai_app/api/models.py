from dataclasses import dataclass, field
import datetime
from pydantic import BaseModel
from typing import Optional


@dataclass
class User:
    user_id: str
    email: str
    slack_id: str


@dataclass
class Agent:
    user_id: str
    fields_descriptions: str
    start_date_dataset: datetime.datetime
    end_date_dataset: datetime.datetime


@dataclass
class Question:
    query: str
    user_id: str
    slack_id: str
    llm_type: str


class AgentResponse(BaseModel):
    response: str
    tokens_used: int
    total_cost: float
    response_type: str
    last_code_executed: str
    explanation: str
    conversation_id: str
    #dataframe: Optional[dict] = None


class Feedback(BaseModel):
    llm: str
    user_id: str
    question: str
    answer: str
    timestamp: datetime.datetime
    tokens_used: int
    total_cost: float
    is_negative_feedback: bool
    feedback: str


class TestedQuestions(BaseModel):
    questions: dict
