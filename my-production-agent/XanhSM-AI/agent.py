from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Any, Iterable, TypedDict
# from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from tool import create_ticket,  lookup_trip

LOGGER = logging.getLogger("XanhSM")
PROMPT_PATH = Path(__file__).with_name("system_promt.txt")
MODEL_NAME = "gpt-4o-mini"
# MODEL_NAME="gemini-2.5-flash"


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def _setup_logging() -> None:
    LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("XanhSM.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    LOGGER.handlers = []
    LOGGER.addHandler(file_handler)


def _load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    t = item["text"].strip()
                    if t:
                        parts.append(t)
        return "\n".join(parts).strip()
    return str(content).strip()


def _log_tool_calls(tool_calls: Iterable[dict[str, Any]] | None) -> None:
    if not tool_calls:
        LOGGER.debug("❌ Không gọi tool")
        return
    LOGGER.debug("✅ GỌI TOOL")
    for tc in tool_calls:
        name = tc.get("name", "<unknown>")
        args = tc.get("args", {})
        LOGGER.debug("→ %s(%s)", name, args)


def build_graph() -> Any:
    load_dotenv(override=True)

    system_prompt = _load_system_prompt()
    tools_list = [create_ticket,  lookup_trip]
    memory = MemorySaver()

    llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
    # llm= ChatGoogleGenerativeAI(model=MODEL_NAME,temperature=0)
    llm_with_tools = llm.bind_tools(tools_list)

    def agent_node(state: AgentState) -> dict[str, list[BaseMessage]]:
        msgs = state["messages"]

        # Inject system prompt
        if not msgs or not isinstance(msgs[0], SystemMessage):
            msgs = [SystemMessage(content=system_prompt)] + msgs

        # 🔥 LOG INPUT (ghi file, không print)
        LOGGER.debug("===== DEBUG MESSAGES =====")
        for m in msgs:
            LOGGER.debug(f"{type(m).__name__}: {getattr(m, 'content', '')}")
        LOGGER.debug("===== END =====")

        response = llm_with_tools.invoke(msgs)

        # 🔥 LOG RAW RESPONSE
        LOGGER.debug("===== RAW RESPONSE =====")
        LOGGER.debug(response)
        LOGGER.debug("===== END =====")

        # 🔥 LOG DECISION
        if getattr(response, "tool_calls", None):
            LOGGER.debug("➡️ Agent quyết định: GỌI TOOL")
        else:
            LOGGER.debug("➡️ Agent quyết định: KHÔNG gọi tool")

        _log_tool_calls(getattr(response, "tool_calls", None))

        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)

    tools_node = ToolNode(tools_list)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=memory)


def main() -> None:
    _setup_logging()
    graph = build_graph()

    print("=" * 60)
    print("xanhsm")
    print("Gõ 'quit' để thoát")
    print("=" * 60)

    thread_id = "test-session"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        user_input = input("Bạn: ").strip()
        if user_input.lower() in {"quit", "exit", "bye"}:
            break

        result: AgentState = graph.invoke(
            {"messages": [("human", user_input)]},
            config=config
        )
        final_msg = result["messages"][-1]

        # 👉 CHỈ HIỂN THỊ OUTPUT
        print(f"\nTrợ lý Xanh: {_content_to_text(getattr(final_msg, 'content', ''))}")


if __name__ == "__main__":
    main()