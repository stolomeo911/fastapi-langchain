from fastapi import APIRouter, HTTPException
from ..models import Message, ModelResponse, Dataset
from langchain.memory import ConversationBufferWindowMemory
import os
import logging
from ...core.agent_tools import call_pandasai, generate_journal_article, generate_suggested_questions
from ...llm.llm import llm_cohere
from ...core.agent import create_cohere_agent
from fastapi import APIRouter, HTTPException
from ..models import Dataset, SuggestedQuestionsResponse
from langchain.schema import HumanMessage
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "ai-content-creator"

router = APIRouter()

# Dictionary to store memory objects for each session
session_memories = {}


memory = ConversationBufferWindowMemory(k=4)

agent = create_cohere_agent(llm_cohere, [generate_suggested_questions,
                                         call_pandasai, generate_journal_article])


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
        response = agent.invoke({"input": message.user_input,"user_id": message.user_id, "preamble":"You are an automatic content creator from dataset""You first perform data analysis using call_pandasai tool and then generate an journal"" article using generate_journal_article"})

        logger.debug(memory.load_memory_variables({}))

        model_response = ModelResponse(user_input=message.user_input, response=response['output'])
        return model_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def format_metadata(metadata: dict) -> str:
    """Format the metadata dictionary into a readable string for the LLM prompt."""
    # Format columns and data types
    columns = metadata.get('columns', [])
    data_types = metadata.get('data_types', [])
    summary_stats = metadata.get('summary_stats', {})

    columns_info = "\n".join([f"- {col} ({dtype})" for col, dtype in zip(columns, data_types)])

    # Format summary statistics
    summary_stats_str = "Summary Statistics:\n"
    for col, stats in summary_stats.items():
        summary_stats_str += f"\n{col}:\n"
        for stat_name, value in stats.items():
            summary_stats_str += f"  - {stat_name}: {value}\n"

    metadata_str = f"Columns and Data Types:\n{columns_info}\n\n{summary_stats_str}"
    return metadata_str


@router.post("/ask_suggested_questions", response_model=SuggestedQuestionsResponse)
async def ask_suggested_questions(dataset: Dataset) -> SuggestedQuestionsResponse:
    logger.info('Generating suggested questions based on dataset metadata...')
    try:
        # Extract metadata from the dataset
        metadata = dataset.metadata  # This is a dictionary as per extract_metadata function

        # Format the metadata into a string for the LLM prompt
        metadata_str = format_metadata(metadata)

        # Construct the prompt for the LLM
        prompt = (
            f"Given the following dataset metadata, generate the most interesting and insightful questions "
            f"that can be asked about this dataset to help with data analysis and understanding:\n\n{metadata_str}\n\nQuestions:"
        )

        # Create a HumanMessage for the chat model
        messages = [HumanMessage(content=prompt)]

        # Use the LLM to generate a response
        response = llm_cohere(messages)

        # Process the LLM response to extract the questions
        questions = response.content.strip().split('\n')
        questions = [q.strip('- ').strip() for q in questions if q.strip()]

        # Create and return the response
        suggested_questions_response = SuggestedQuestionsResponse(questions=questions)
        return suggested_questions_response
    except Exception as e:
        logger.error(f"Error generating suggested questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))