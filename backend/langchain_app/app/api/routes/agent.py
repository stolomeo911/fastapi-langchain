from fastapi import APIRouter, HTTPException
from ..models import Message, ModelResponse
from langchain.memory import ConversationBufferWindowMemory
import os
import logging
from ...core.agent_tools import call_pandasai, generate_journal_article
from ...llm.llm import llm_cohere
from ...core.agent import create_cohere_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "ai-content-creator"

router = APIRouter()

# Dictionary to store memory objects for each session
session_memories = {}

memory = ConversationBufferWindowMemory(k=4)

agent = create_cohere_agent(llm_cohere, [call_pandasai, generate_journal_article])


@router.post("/chat")
async def chat(message: Message) -> ModelResponse:
    logger.info('Chat request has been requested..')
    try:
        session_id = message.session_id

        # Retrieve or create memory for the session
        if session_id not in session_memories:
            session_memories[session_id] = ConversationBufferWindowMemory(k=4)
        memory = session_memories[session_id]

        # Generate the model's respons
        response = agent.invoke({
            "input": message,
            "preamble":
                "You are an automatic content creator from dataset"
                "You first perform data analysis using call_pandasai tool and then generate an journal"
                " article using generate_journal_article"
        })

        logger.debug(memory.load_memory_variables({}))

        model_response = ModelResponse(user_input=message.user_input, response=response['output'])
        return model_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))