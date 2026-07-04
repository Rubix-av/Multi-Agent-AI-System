
import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
COMMAND_PATH = r"D:\Akshobh\Learning and Career\Artificial Intelligence\AI Engineering\Agentic AI\multi_agent_ai_system\aviationstack-mcp\.venv\Scripts\python.exe"

client = MultiServerMCPClient(
    {
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
        }
    }
)

async def main():
    tools = await client.get_tools()

    print("\nAvailable Tools:\n")

    for tool in tools:
        print(tool.name)

asyncio.run(main())
