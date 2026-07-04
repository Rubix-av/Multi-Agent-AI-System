
import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
COMMAND_PATH = r"D:\Akshobh\Learning and Career\Artificial Intelligence\AI Engineering\Agentic AI\multi_agent_ai_system\aviationstack-mcp\.venv\Scripts\python.exe"
ARGS = r"D:\Akshobh\Learning and Career\Artificial Intelligence\AI Engineering\Agentic AI\multi_agent_ai_system\tools\weather_mcp_server.py"

client = MultiServerMCPClient(
    {
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

# tool discovering
async def main():

    print("Loading tools...")

    tools = await client.get_tools()

    print("Tools loaded!")

    for tool in tools:
        print(tool.name)

if __name__ == "__main__":
    asyncio.run(main())
