from core.agent import set_nodes_for_ai_content_creator, set_agent_graph
from core.agent_state import AgentState
from core.agent_tools import call_pandasai, generate_journal_article
from llm.llm import llm, llm_cohere
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
import os
from core.agent import create_cohere_agent

os.environ["LANGCHAIN_TRACING_V2"] = 'true'
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "ai-content-creator"


pandasai_agent_node, article_agent_node = set_nodes_for_ai_content_creator(llm)

workflow = set_agent_graph(AgentState, pandasai_agent_node, article_agent_node)

graph = workflow.compile()

# Get the Mermaid graph definition
mermaid_graph = graph.get_graph(xray=True).draw_mermaid()

"""
# Print the Mermaid graph definition to the console
events = graph.stream(
    {
        "messages": [
            HumanMessage(
                content="Create a table with the top 10 countries with highest temperature increase in the last 10 years."
                        "Then create a journal article describing this table and its insight, then finish."
            )
        ],
    },
    # Maximum number of steps to take in the graph
    {"recursion_limit": 150},
)
for s in events:
    print(s)
    print("----")
"""

agent = create_cohere_agent(llm_cohere, [call_pandasai, generate_journal_article])

agent.invoke({
   "input": "Which is the country with highest temperature increase in the last 50 years?. then the one with the least increase,"
            ". Then the average increase across all countries."
                        "Then create a journal article describing those evidence of max 200 words",
   "preamble":
                "You are an automatic content creator from dataset"
                "You first perform data analysis using call_pandasai tool and then generate an journal article using generate_journal_article"
})