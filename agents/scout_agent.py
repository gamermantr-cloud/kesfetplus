"""LangGraph Scout Agent.

Discovers real-world place candidates for a city using the Google Places
API (New) Text Search endpoint. Falls back to a "not configured" status
when GOOGLE_PLACES_API_KEY is not set, so the graph still runs end-to-end
without a key.
"""

import os
from typing import TypedDict

import requests
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

load_dotenv()

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


class Place(TypedDict):
    name: str
    address: str
    rating: float | None


class ScoutState(TypedDict):
    city: str
    status: str
    message: str
    places: list[Place]


def _search_places(city: str, api_key: str) -> list[Place]:
    response = requests.post(
        PLACES_SEARCH_URL,
        json={"textQuery": f"popular restaurants and places in {city}"},
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return [
        {
            "name": place.get("displayName", {}).get("text", ""),
            "address": place.get("formattedAddress", ""),
            "rating": place.get("rating"),
        }
        for place in data.get("places", [])
    ]


def scout_node(state: ScoutState) -> ScoutState:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")

    if not api_key:
        return {
            "city": state["city"],
            "status": "not_configured",
            "message": "GOOGLE_PLACES_API_KEY not set - add it to .env to enable real search.",
            "places": [],
        }

    try:
        places = _search_places(state["city"], api_key)
    except requests.RequestException as exc:
        return {
            "city": state["city"],
            "status": "error",
            "message": f"Google Places request failed: {exc}",
            "places": [],
        }

    return {
        "city": state["city"],
        "status": "ready",
        "message": f"Found {len(places)} discovery candidates.",
        "places": places,
    }


def build_scout_graph():
    graph = StateGraph(ScoutState)
    graph.add_node("scout", scout_node)
    graph.set_entry_point("scout")
    graph.add_edge("scout", END)
    return graph.compile()


def run_scout_agent(city: str) -> dict:
    graph = build_scout_graph()
    return graph.invoke({"city": city, "status": "", "message": "", "places": []})


if __name__ == "__main__":
    result = run_scout_agent("Istanbul")
    print(result)
