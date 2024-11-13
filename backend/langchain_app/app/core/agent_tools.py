import logging

import pandas as pd

from shared_libraries.make_request import parse_multipart
from langchain_core.tools import tool
import requests
from .consts import PANDASAI_URL
from typing import Annotated
from ..llm.llm import llm_cohere


@tool
def call_pandasai(
        question: Annotated[str, "This is the question to be used for the paylaod to call the api of pandasai"],
):
    """Use this to call pandasai api that will response to you with a json data
    The result is visible to the user."""
    payload = {"query": question, "user_id": 'try',
               "dataset": 'Temperature Change by Country', "llm_type": 'gpt'}
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


def extract_metadata(df: pd.DataFrame):
    """Extract metadata from the dataframe including column names, data types, and summary statistics."""
    metadata = {
        'columns': df.columns.tolist(),
        'data_types': df.dtypes.apply(lambda x: str(x)).tolist(),
        'summary_stats': df.describe(include='all').to_dict()
    }
    return metadata


@tool
def generate_suggested_questions(metadata):
    """Generate a prompt for the LLM to suggest questions based on the metadata."""
    columns = metadata['columns']
    data_types = metadata['data_types']
    summary = metadata['summary_stats']

    prompt = f"""
    Based on the following dataset metadata, suggest questions the user can ask for analysis 
    to use in a data journal article.

    Columns: {columns}
    Data types: {data_types}
    Summary Statistics: {summary}

    Provide a list of questions to explore the dataset and create a story telling
    based
    """

    return prompt


# Define the tool for calling the LLM to generate a journal article
@tool
def generate_journal_article(
        data: Annotated[dict, "This is the data received from PandasAI"]
):
    """Use this to call the LLM to generate a journal article based on the data received."""

    # Create a detailed prompt for the LLM
    prompt = f"""
    Write a detailed journal article based on the following data. The article should include a title, an introduction,
     key findings, a discussion of current trends and future projections, and a conclusion. 
     The style should be similar to articles on Our World in Data, including a byline, date, and a section encouraging 
     citation and reuse of the work. The article should be maximum 250 words. Use bold to highlights most important findings and insights.
        Here is the data:
    {data}

    Article format:

    Title: [Insert Title Based on Data]

    By: [Your Name]
    [Current Date]
    Cite this article
    Reuse our work freely

    Introduction:
    Provide a brief overview of the data analysis, highlighting the main focus and the importance of the findings. 
    Discuss why this topic is significant and what the reader can expect to learn from the article.

    Key Findings:
    - Summarize the most significant findings from the data. This can include highest and lowest values, averages,
     and any notable trends or anomalies. Provide context and explanations for these findings,
      making sure they are accessible to a general audience.

    Current Trends and Future Projections:
    Discuss the current state of the topic based on the data provided. Include any relevant statistics, graphs, or
     charts. Then, make projections about how these trends might change in the future. Consider factors such as
      technological advancements, policy changes, and socio-economic influences that could impact these trends.

    Implications:
    Explain the broader implications of the findings. Discuss how different regions or demographics might be affected 
    and what the potential consequences are. Include considerations of geographical, environmental, and socio-economic 
    factors. 

    Conclusion:
    Summarize the key points discussed in the article. Emphasize the broader implications of the findings and the
     importance of ongoing research and monitoring. Encourage actions or policies that could address the issues raised.

    Remember to follow the style and tone of Our World in Data articles. Make sure the article is informative, 
    well-structured, and engaging for the reader.
    """

    logging.debug(f"Generated prompt for LLM: {prompt}")

    # Call the LLM to generate the article
    article = llm_cohere.invoke(prompt)

    logging.debug(f"Generated article: {article}")
    return article
