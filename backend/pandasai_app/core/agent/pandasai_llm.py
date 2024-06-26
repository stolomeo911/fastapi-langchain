import os
from pandasai.llm.local_llm import LocalLLM
from pandasai.llm.openai import OpenAI
from pandasai.llm import BambooLLM
from shared_libraries.utils import _fetch_secret_key


llms = {
    'local': LocalLLM(api_base="http://localhost:11434/v1", model="mistral"),
    'gpt': OpenAI(api_token=_fetch_secret_key('GPT_API_KEY', os.environ['ENV']), temperature=0, seed=26, model='gpt-4o-2024-05-13'),
    'bamboo': BambooLLM(api_key=_fetch_secret_key('PANDASAI_API_KEY', os.environ['ENV']))
}


def get_llm(type='local'):
    return llms[type]
