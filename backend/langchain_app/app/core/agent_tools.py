import os

from shared_libraries.make_request import parse_multipart
from langchain_core.tools import tool
import requests
from .consts import PANDASAI_URL
from typing import Annotated
from langchain_openai import ChatOpenAI

@tool
def call_pandasai(
        question: Annotated[str, "This is the question to be used for the paylaod to call the api of pandasai"],
):
    """Use this to call pandasai api that will response to you with a json data
    The result is visible to the user."""
    payload = {"query": question, "user_id": 'try',
               "slack_id": 'aaaa', "llm_type": 'gpt'}
    print(payload)
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""

    #with aiohttp.ClientSession() as session:
    #    data = make_request(session, 'get', f'{PANDASAI_URL}/agent/ask_question',
    #                              json=payload)
    response = requests.get(f'{PANDASAI_URL}/agent/ask_question', json=payload)
    content_type = response.headers.get('Content-Type', '')
    if 'multipart/form-data' in content_type:
        return parse_multipart(response)
    else:
        return response.json()


# Define the tool for calling the LLM to generate a journal article
@tool
def generate_journal_article(
    data: Annotated[dict, "This is the data received from PandasAI"],
):
    """Use this to call the LLM to generate a journal article based on the data received."""
    llm = ChatOpenAI(model="gpt-4o-2024-05-13",
                     openai_api_key=os.environ['GPT_API_KEY'])
    prompt = f"Create a journal article based on the following data:\n\n{data}"
    article = llm.call_as_llm(prompt)
    return article