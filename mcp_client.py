
from langchain_groq import ChatGroq
import os
import asyncio

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
COMMAND_PATH = r"D:\Akshobh\Learning and Career\Artificial Intelligence\AI Engineering\Agentic AI\multi_agent_ai_system\aviationstack-mcp\.venv\Scripts\python.exe"
ARGS = r"D:\Akshobh\Learning and Career\Artificial Intelligence\AI Engineering\Agentic AI\multi_agent_ai_system\tools\weather_mcp_server.py"

llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

client = MultiServerMCPClient(
    {
        # Remote MCP Server
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },

        # Local MCP Server
        "aviationstack": {
            "transport": "stdio",
            "command": COMMAND_PATH,
            "args": [
                "-m",
                "aviationstack_mcp",
                "mcp",
                "run"
            ],
            "env": {
                "AVIATIONSTACK_API_KEY": AVIATIONSTACK_API_KEY,
            }
        },

        # Custom MCP Server
        "weather": {
            "transport": "stdio",
            "command": COMMAND_PATH,
            "args": [
                ARGS
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY,
            }
        }
    }
)

# async def main():
#     tools = await client.get_tools()
#     print("\nAvailable MCP Tools:\n")
#     for tool in tools:
#         print(tool.name)

async def main():
    tools = await client.get_tools()
    print("\nAvailable MCP Tools:\n")
    
    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )
    result = await search_tool.ainvoke(
        {
            "query": "Best Hotels in Delhi"
        }
    )
    print(result)

search_tool = None
aviation_tools = {}

async def initialize_mcp():
    """
    Connect to MCP server and discover tools once.
    """

    global search_tool
    global aviation_tools

    if search_tool is not None:
        return

    tools = await client.get_tools()

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )

    aviation_tool = next(
        tool
        for tool in tools
        if tool.name != "tavily_search"
    )

async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke(
        {
            "query": query
        }
    )
    return result

async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    
    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

async def get_airports():

    await initialize_mcp()

    tool = aviation_tools.get("list_airports")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result

async def get_airlines():

    await initialize_mcp()

    tool = aviation_tools.get("list_airlines")

    if not tool:
        return "Airport tool unavailable"

    result = await tool.ainvoke({})

    return result



def extract_destination(query: str):

    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)

    return response.content.strip()




weather_tool = None
forecast_tool = None

async def initialize_weather_tools():

    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )

async def weather_mcp_search(city: str):
    
    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )

async def forecast_mcp_search(city: str):

    await initialize_weather_tools()

    return await forecast_tool.ainvoke(
        {
            "city": city
        }
    )

if __name__ == "__main__":
    asyncio.run(main())

