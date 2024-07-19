import aiohttp
from langchain_core.tools import tool
from shared_libraries.make_request import make_request
from .consts import PANDASAI_URL
from typing import Annotated


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
    with aiohttp.ClientSession() as session:
        data = make_request(session, 'get', f'{PANDASAI_URL}/agent/ask_question',
                                  json=payload)
    return data