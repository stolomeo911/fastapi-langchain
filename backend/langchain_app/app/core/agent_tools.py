import aiohttp

from langchain_core.tools import tool
from shared_libraries.make_request import make_request

@tool
async def call_pandasai(
    payload,
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    async with aiohttp.ClientSession() as session:
        data = await make_request(session, 'get', f'{URL}/agent/ask_question',
                                  json=payload)
    return data