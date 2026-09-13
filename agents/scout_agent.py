"""Minimal LangGraph Scout Agent.

This agent does not connect to the internet or any external service yet.
Its only job right now is to prove that the LangGraph foundation works.
"""

from typing import TypedDict

from langgraph.graph import StateGraph, END


class ScoutState(TypedDict):
    city: str
    status: str
    message: str


def scout_node(state: ScoutState) -> ScoutState:
    return {
        "city": state["city"],
        "status": "ready",
        "message": "Scout agent is ready to search for discovery candidates.",
    }


def build_scout_graph():
    graph = StateGraph(ScoutState)
    graph.add_node("scout", scout_node)
    graph.set_entry_point("scout")
    graph.add_edge("scout", END)
    return graph.compile()


def run_scout_agent(city: str) -> dict:
    graph = build_scout_graph()
    return graph.invoke({"city": city, "status": "", "message": ""})


if __name__ == "__main__":
    result = run_scout_agent("Istanbul")
    print(result)
