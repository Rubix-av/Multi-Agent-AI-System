
import sys
import asyncio
import os
from typing import TypedDict, Annotated
import operator

sys.stdout.reconfigure(encoding='utf-8')

import json
import ast

def format_weather_info(weather_data, forecast_data):
    def to_dict(val):
        if not val:
            return {}
        if isinstance(val, dict):
            return val
        if isinstance(val, str):
            val_stripped = val.strip()
            if (val_stripped.startswith('{') and val_stripped.endswith('}')) or (val_stripped.startswith('[') and val_stripped.endswith(']')):
                try:
                    return json.loads(val_stripped)
                except Exception:
                    try:
                        return ast.literal_eval(val_stripped)
                    except Exception:
                        pass
        return {}

    w_dict = to_dict(weather_data)
    f_dict = to_dict(forecast_data)

    markdown_parts = []

    if w_dict and isinstance(w_dict, dict) and "temperature_c" in w_dict:
        markdown_parts.append("### 🌡️ Current Weather")
        markdown_parts.append(f"- **City**: {w_dict.get('city', 'Unknown')}")
        markdown_parts.append(f"- **Condition**: {str(w_dict.get('condition', 'Unknown')).capitalize()}")
        markdown_parts.append(f"- **Temperature**: {w_dict.get('temperature_c')}°C (Feels Like: {w_dict.get('feels_like_c')}°C)")
        markdown_parts.append(f"- **Humidity**: {w_dict.get('humidity')}%")
        markdown_parts.append(f"- **Wind Speed**: {w_dict.get('wind_speed')} m/s")
    else:
        markdown_parts.append("### 🌡️ Current Weather")
        markdown_parts.append(str(weather_data))

    markdown_parts.append("")

    if f_dict and isinstance(f_dict, dict) and "forecast" in f_dict:
        markdown_parts.append("### 📅 Weather Forecast")
        for item in f_dict.get("forecast", []):
            dt = item.get("datetime", "Unknown")
            temp = item.get("temperature", "Unknown")
            weather = str(item.get("weather", "Unknown")).capitalize()
            markdown_parts.append(f"- **{dt}**: {temp}°C, {weather}")
    else:
        markdown_parts.append("### 📅 Weather Forecast")
        markdown_parts.append(str(forecast_data))

    return "\n".join(markdown_parts)

import psycopg
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (AnyMessage, HumanMessage, SystemMessage, AIMessage)
from langchain_groq import ChatGroq

# imports needed before implementation of MCP server
# from tools.tavily_tool import tavily_search
# from tools.flight_tool import search_flights


from mcp_client import tavily_mcp_search, aviation_mcp_call, get_airlines, get_airports, weather_mcp_search, forecast_mcp_search, extract_destination
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
    weather_results: str

# Flight Agent
# def flight_agent(state: TravelState):
#     query = state["user_query"]
#     flight_data = search_flights(query)
#     return {
#         "flight_results": flight_data,
#         "messages": [
#             AIMessage(content=f"Flight results fetched")
#         ],
#         "llm_calls": state.get("llm_calls", 0) + 1
#     }



FLIGHT_AGENT_PROMPT = """
You are a travel flight expert.

User Query:
{query}

Airport Information:
{airport_data}

Airline Information:
{airline_data}

Generate:

1. Likely departure airport
2. Likely arrival airport
3. Airlines serving this route
4. Typical flight duration
5. Estimated airfare range
6. Peak season pricing warning
7. Booking advice

Return concise travel guidance
"""

HOTEL_AGENT_PROMPT = """
You are a travel accommodation expert.

User Query:
{query}

Web Search Results:
{search_results}

Generate a well-formatted markdown list of the best hotel options. For each hotel, include:
1. Hotel Name
2. A brief description or key features
3. Price range or rating (if available)

Return concise travel guidance formatted cleanly in Markdown. Do not include raw JSON.
"""

WEATHER_AGENT_PROMPT = """
You are a weather information specialist for travelers.

Destination City:
{city}

Current Weather Data:
{weather_data}

5-Day Forecast Data:
{forecast_data}

Generate a well-formatted markdown weather report. Include:

### 🌡️ Current Weather
- City name
- Current temperature (°C) and "feels like" temperature
- Weather condition (e.g., clear sky, light rain)
- Humidity percentage
- Wind speed

### 📅 5-Day Forecast
For each forecast entry, show:
- Date and time
- Temperature (°C)
- Weather condition

Use bullet points, bold labels, and weather emojis for readability.
Do NOT include raw JSON or code blocks. Format everything as clean, human-readable Markdown.
"""

# Flight Agent
def flight_agent(state: TravelState):
    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_query"]

    try:
        airports = asyncio.run(
            aviation_mcp_call(
                "list_airports"
            )
        )

        airlines = asyncio.run(
            aviation_mcp_call(
                "list_airlines"
            )
        )

        prompt = FLIGHT_AGENT_PROMPT.format(
            query=query,
            airport_data=str(airports)[:3000],
            airline_data=str(airlines)[:3000]
        )

        response = llm.invoke([
            SystemMessage(
                content="You are an expert travel flight planner."
            ),
            HumanMessage(content=prompt)
        ])

        flight_data = response.content

    except Exception as e:
        flight_data = f"Flight information unavailable: {str(e)}"

    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(
                content="Flight recommendations generated"
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['user_query']}"

    try:
        hotel_results = asyncio.run(
            tavily_mcp_search(query)
        )
        
        prompt = HOTEL_AGENT_PROMPT.format(
            query=state["user_query"],
            search_results=hotel_results
        )
        
        response = llm.invoke(prompt)
        hotel_data = response.content
        
    except Exception as e:
        hotel_data = f"Could not retrieve hotel data: {e}"
    
    return {
        "hotel_results": hotel_data,
        "messages": [
            AIMessage(content="Hotel information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def weather_agent(state: TravelState):

    city = extract_destination(state["user_query"])

    try:
        weather_data = asyncio.run(
            weather_mcp_search(city)
        )

        forecast_data = asyncio.run(
            forecast_mcp_search(city)
        )

        prompt = WEATHER_AGENT_PROMPT.format(
            city=city,
            weather_data=weather_data,
            forecast_data=forecast_data
        )

        response = llm.invoke(prompt)
        formatted_weather = response.content

    except Exception as e:
        formatted_weather = f"Could not retrieve weather data: {e}"

    return {
        "weather_results": formatted_weather,
        "messages": [
            AIMessage(content="Weather information fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

def itinerary_agent(state: TravelState):
    prompt = f"""
    Create a travel itinerary.
    User Query:
    {state["user_query"]}
    
    Flight Results:
    {state["flight_results"]}
    
    Hotel Results:
    {state["hotel_results"]}

    Weather Information:
    {state["weather_results"]}
    """
    
    response = llm.invoke([
        SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(content=prompt)
    ])
    
    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# setup graph
graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("itinerary_agent", itinerary_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "weather_agent")
graph.add_edge("weather_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", END)

# establish database connection
_conn = psycopg.connect(DATABASE_URL)
_conn.autocommit = True

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "user_akshobh"
        }
    }
    
    
    user_input = input("Enter travel request: ")
    
    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )
    
    print("\nFINAL RESPONSE:\n")
    
    for msg in result["messages"]:
        print(msg.content)
