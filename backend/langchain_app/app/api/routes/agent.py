from fastapi import APIRouter, HTTPException
from ..models import Message, ModelResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import ConversationChain
from ...llm.llm import llm
from langchain.memory import ConversationBufferWindowMemory
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

# Dictionary to store memory objects for each session
session_memories = {}

memory = ConversationBufferWindowMemory(k=4)


@router.get("/chat")
async def chat(message: Message) -> ModelResponse:
    logger.info('Chat request has been requested..')
    try:
        session_id = message.session_id

        # Retrieve or create memory for the session
        if session_id not in session_memories:
            session_memories[session_id] = ConversationBufferWindowMemory(k=4)
        memory = session_memories[session_id]

        # Generate the model's respons
        conversation = ConversationChain(llm=llm, verbose=True, memory=memory)

        response = conversation.predict(input=message.user_input)

        logger.debug(memory.load_memory_variables({}))

        # Parse the response to update the sources
        response_data = json.loads(response)
        if "sources" in response_data:
            response_data["sources"] = [f"http://{source}" if not source.startswith("http") else source for source in
                                        response_data["sources"]]

        # Convert the updated response back to a JSON string
        updated_response = json.dumps(response_data)

        model_response = ModelResponse(user_input=message.user_input, response=updated_response)
        return model_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# You can use this debug method to check how the (raw) output of the model looks like
@router.get("/debug")
async def debug():
    prompt = ChatPromptTemplate.from_template("Answer to the user's question: {q}")
    chain = prompt | llm
    return chain.invoke({"q": "dummy question"})