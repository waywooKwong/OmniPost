# 设置模型 api key
import os
os.environ["DASHSCOPE_API_KEY"] = "sk-5b107470a09d4149928ab97fd316c722"
os.environ["GOOGLE_API_KEY"] = "AIzaSyAfyavDP9XUJrVZanpcTMoj_PxoS5j6Wdw"

from typing import Annotated

from langchain_google_genai import GoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


tool = DuckDuckGoSearchResults(max_results=2)
tools = [tool]
llm = GoogleGenerativeAI(model="gemini-2.0-flash")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

# attention 1: 直接使用 ToolNode 打包工具结点
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# attention 2: 使用 tools_condition 构建条件边，不需要手写 router 函数
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()