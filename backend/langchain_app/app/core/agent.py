from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from .agent_tools import call_pandasai
from langgraph.graph import END, StateGraph, START
import functools
from langgraph.prebuilt import ToolNode
from typing import Literal


def create_agent(llm, tools, system_message: str):
    """Create an agent."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful AI assistant, collaborating with other assistants."
                " Use the provided tools to progress towards answering the question."
                " If you are unable to fully answer, that's OK, another assistant with different tools "
                " will help where you left off. Execute what you can to make progress."
                " If you or any of the other assistants have the final answer or deliverable,"
                " prefix your response with FINAL ANSWER so the team knows to stop."
                " You have access to the following tools: {tool_names}.\n{system_message}",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    prompt = prompt.partial(system_message=system_message)
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
    return prompt | llm.bind_tools(tools)


def add_agent_node(state, agent, name):
    result = agent.invoke(state)
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(result, name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }


def set_nodes_for_ai_content_creator(llm):
    pandasai_agent = create_agent(
        llm,
        [call_pandasai],
        system_message="Any charts / table / string you display will be visible by the user.",
    )
    pandasai_agent_node = functools.partial(add_agent_node, agent=pandasai_agent, name="PandasAiAnalyst")

    article_video_agent = create_agent(
        llm,
        [],  # Assuming this agent does not need additional tools
        system_message="You are tasked with creating a journal article from the data analysis of maximum 250 words.",
    )
    article_agent_node = functools.partial(add_agent_node, agent=article_video_agent, name="ArticleCreator")

    return pandasai_agent_node, article_agent_node


def router(state) -> Literal["call_tool", "__end__", "continue"]:
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # The previous agent is invoking a tool
        return "call_tool"
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        return "__end__"
    return "continue"


def set_agent_graph(agent_state, pandasai_agent_node, article_agent_node):
    # Define the state graph
    workflow = StateGraph(agent_state)

    workflow.add_node("PandasAiAnalyst", pandasai_agent_node)
    workflow.add_node("ArticleCreator", article_agent_node)

    tools = [call_pandasai]
    tool_node = ToolNode(tools)
    workflow.add_node("call_tool", tool_node)

    workflow.add_conditional_edges(
        "PandasAiAnalyst",
        router,
        {"continue": "ArticleCreator", "call_tool": "call_tool", "__end__": END},
    )
    workflow.add_conditional_edges(
        "ArticleCreator",
        router,
        {"continue": "PandasAiAnalyst", "call_tool": "call_tool", "__end__": END},
    )

    workflow.add_conditional_edges(
        "call_tool",
        # Each agent node updates the 'sender' field
        # the tool calling node does not, meaning
        # this edge will route back to the original agent
        # who invoked the tool
        lambda x: x["sender"],
        {
            "PandasAiAnalyst": "PandasAiAnalyst",
            "ArticleCreator": "ArticleCreator",
        },
    )

    workflow.add_edge(START, "PandasAiAnalyst")

    return workflow

