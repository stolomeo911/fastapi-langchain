import os

from pandasai import Agent
from pandasai.connectors import PandasConnector
import matplotlib

from pandasai.helpers.openai_info import get_openai_callback
import pandas as pd
import yaml
from yaml import Loader
import typer
from shared_libraries.utils import setup_logger
from backend.pandasai_app.core.agent.pandasai_llm import get_llm
from backend.pandasai_app.core.agent.pandasai_vector_store import get_pandasai_vector_store
from backend.pandasai_app.core.agent.agent_skills import plot_daily_run_rate_leads
import warnings
warnings.simplefilter('ignore')
matplotlib.use('Agg')

logger = setup_logger(__name__)

app = typer.Typer()


def connect_to_db():
    from pandasai.connectors import SQLConnector

    postgres_connector = SQLConnector(
        config={
            "host": os.environ['REDSHIFT_HOST'],
            "port": 5439,
            "database":  os.environ['REDSHIFT_DATABASE'],
            "username": os.environ['REDSHIFT_USER'],
            "password": os.environ['REDSHIFT_PASSWORD'],
            "table": "ml_output.apollo_feedback_logs"
        }
    )
    return postgres_connector


@app.command()
def get_pandasai_agent(connector, config, vector_store=None, description=None):
    if vector_store is None:
        return Agent(dfs=connector, config=config, description=description)
    else:
        return Agent(dfs=connector, config=config, vectorstore=vector_store,
                     description=description)


@app.command()
def get_agent(source='csv', mode='pandas_generator', add_skills=True) -> Agent:
    config = yaml.load(open('backend/pandasai_app/core/agent/training/config.yml'), Loader=Loader)
    metadata = yaml.load(open(config['metadata']), Loader=Loader)

    if source == 'csv':
        df = pd.read_csv(config['file_path'])
    elif source == 'pickle':
        df = pd.read_pickle(config['file_path'])
    else:
        raise NotImplementedError

    connector = PandasConnector({"original_df": df}, field_descriptions=metadata)
    llm_type = config['llm_type']
    llm = get_llm(llm_type)
    vector_store = get_pandasai_vector_store(llm_type)

    agent_config = {"llm": llm,
              **config['agent_config']}
    if mode == 'pandas_generator':
        agent = get_pandasai_agent(connector, agent_config, vector_store, config['description'])
    elif mode == 'sql_generator':
        sql_connector = connect_to_db()
        agent = get_pandasai_agent(sql_connector, agent_config, vector_store, None)
    else:
        raise NotImplementedError

    if add_skills:
        agent.add_skills(plot_daily_run_rate_leads)
    return agent


def get_last_status_query(agent):
    return agent.pipeline.query_exec_tracker._steps[-1]['success']


def get_response_type(agent):
    return agent.pipeline.query_exec_tracker._response['value']['type']


async def get_dataframe_from_response(agent):
    return pd.DataFrame(agent.pipeline.query_exec_tracker._response['value']['value']['rows'],
                        columns=agent.pipeline.query_exec_tracker._response['value']['value']['headers'])


@app.command()
async def chat_with_agent(agent, question, llm, max_retries=1):
    logger.info(f'The agent memory is {agent.context.memory.get_messages()}')
    #response = ''
    tokens_used = 0
    total_cost = 0
    success_status = None

    #for retry_count in range(max_retries):
        #logger.debug(f'Performing retry {str(retry_count + 1)} for query {question}')
    if llm == 'gpt':
        with get_openai_callback() as cb:
            response = agent.chat(question)
            tokens_used += cb.total_tokens
            total_cost += cb.total_cost
    else:
        response = agent.chat(question)
        tokens_used, total_cost = 0, 0

    success_status = get_last_status_query(agent)
    logger.debug(f'Success status is {success_status}')
        #if success_status:
        #    break

        #logger.warning(f'Retry {retry_count + 1}/{max_retries} failed for query: {question}')

    #if not success_status:
    #    logger.error('Query failed after maximum retries')

    response_type = get_response_type(agent)
    logger.info(f'Response type is {response_type}')
    return response, tokens_used, total_cost, response_type


@app.command()
def train_agent() :

    logger.info('Performing training...')
    agent = get_agent()

    q_a_training_dict = yaml.load(open('backend/langchain_app/core/agent/training/q_a_training.yml'), Loader=Loader)
    docs = yaml.load(open('backend/langchain_app/core/agent/training/docs.yml'), Loader=Loader)

    queries = []
    answers = []

    for query, answer in q_a_training_dict.items():
        queries.append(query)
        answers.append(answer)

    agent.train(queries=queries, codes=answers)
    agent.train(docs=docs)

    logger.info('Training completed...')
    return agent


if __name__ == "__main__":
    app()
