from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse
from requests_toolbelt import MultipartEncoder
from typing import Union

from backend.pandasai_app.api.models import Question, AgentResponse, TestedQuestions
import logging
from backend.pandasai_app.core.agent.pandasai_agent import get_agent, chat_with_agent, get_dataframe_from_response
from backend.pandasai_app.core.agent.pandasai_smart_df import get_current_used_pickle
import os
import yaml
from yaml import Loader
import uuid


logger = logging.getLogger(__name__)

router = APIRouter()

#agent = get_agent()

agents = {}

@router.get('/')
async def index():
    return {"status": 200}


@router.get('/ask_question')
async def ask_question(question: Question):
    session_id = question.user_id
    selected_dataset = question.dataset

    logger.info(f"Received request from session {session_id} with dataset {selected_dataset}")

    # Check if an agent exists for this session
    if session_id in agents:
        agent_info = agents[session_id]
        if agent_info['selected_dataset'] != selected_dataset:
            # Dataset has changed, create a new agent with the new dataset
            agent = get_agent(selected_dataset)
            agents[session_id] = {'agent': agent, 'selected_dataset': selected_dataset}
            logger.info(f"Dataset changed for session {session_id}, agent recreated.")
        else:
            # Use existing agent
            agent = agent_info['agent']
            logger.info(f"Using existing agent for session {session_id}.")
    else:
        # No agent exists for this session, create a new one
        agent = get_agent('csv', selected_dataset)
        agents[session_id] = {'agent': agent, 'selected_dataset': selected_dataset}
        logger.info(f"Created new agent for session {session_id}.")

    query = question.query
    final_message = agent.rephrase_query(query) + ''
    logger.info(f'Rephrased query {query} to {final_message}')

    response, tokens_used, total_cost, response_type = await chat_with_agent(agent, final_message, question.llm_type)

    explanation = agent.explain()
    last_code_executed = agent.last_code_executed
    conversation_id = agent.conversation_id

    agent_response = AgentResponse(
        response=str(response),
        tokens_used=tokens_used,
        total_cost=total_cost,
        response_type=response_type,
        last_code_executed=last_code_executed,
        explanation=explanation,
        conversation_id=conversation_id.__str__()
    )

    if response_type == 'dataframe':
        logger.info(f'Assigning data frame to agent response model')
        df = await get_dataframe_from_response(agent)
        agent.response = 'csv'
        #agent_response.dataframe = df.to_json(orient="records")

        # Save dataframe as CSV file
        csv_file_path = f"/tmp/{uuid.uuid4()}.csv"
        df.to_csv(csv_file_path, index=False)

        m = MultipartEncoder(
            fields={
                'agent_response': agent_response.json(),
                'file': (csv_file_path, open(csv_file_path, 'rb'), 'text/csv')
            }
        )
        return Response(m.to_string(), media_type=m.content_type)

    elif response_type == 'plot':
        agent.response = 'plot'

        logger.info(f'Generating plot for agent response')
        # Assuming response contains data for plotting

        m = MultipartEncoder(
            fields={
                'agent_response': agent_response.json(),
                'file': (response, open(response, 'rb'), 'image/png')
            }
        )
        return Response(m.to_string(), media_type=m.content_type)

    else:
        return JSONResponse(content=agent_response.dict())


@router.get('/explain')
async def get_explanation():
    try:
        return agent.explain()
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except TypeError as te:
        logger.error(f"TypeError: {te}")
        raise HTTPException(status_code=400, detail=str(te))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


@router.get('/agent_info')
async def get_agent_info():
    try:
        agent_df = get_current_used_pickle()
        df = agent.context.dfs

        start_date = agent_df['lead_timestamp'].min()
        end_date = agent_df['lead_timestamp'].max()

        # Create a list of bullet points for field descriptions
        field_descriptions = '\n'.join(
            [f"• *{list(field_description.keys())[0]}*: {list(field_description.values())[0]}" for field_description in
             df[0].field_descriptions])

        metadata = {
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.apply(lambda x: str(x)).tolist(),
            'summary_stats': df.describe(include='all').to_dict()
        }

        return {
            "start_date": start_date,
            "end_date": end_date,
            "field_descriptions": field_descriptions,
            "metadata": metadata}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

@router.get('/ask_clarification_question')
async def ask_clarification_quetions(question: Question):
    clarification_questions = agent.clarification_questions(question.query)
    try:
        return {"clarification_questions": clarification_questions}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


@router.post('/clear_memory')
async def clear_agent_memory():
    agent.clear_memory()
    return {"status": 200}


@router.get('/tested_questions/{kpi}', response_model=TestedQuestions)
async def get_questions(kpi: str):
    base_path = 'backend/langchain_app/core/agent/tests'
    file_paths = {
        "leads": os.path.join(base_path, 'leads/questions.yml'),
        "customers": os.path.join(base_path, 'customers/questions.yml'),
        "trials": os.path.join(base_path, 'trials/questions.yml')
    }

    with open(file_paths[kpi], 'r') as file:
        questions = yaml.load(file, Loader=Loader)['questions']

    tested_questions = TestedQuestions(questions=questions)

    return tested_questions
