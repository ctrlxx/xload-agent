import subprocess
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset,StdioServerParameters

from veadk.utils.logger import get_logger

from xload_agent.config import Config

config = Config()
WORKSPACE_PATH = config.workspace_path

logger = get_logger(__name__)

def check_env():
    try:
        result = subprocess.run(
            ["npx", "-v"], capture_output=True, text=True, check=True
        )
        version = result.stdout.strip()
        logger.info(f"Check `npx` command done, version: {version}")
    except Exception as e:
        raise Exception(
            "Check `npx` command failed. Please install `npx` command manually."
        ) from e

check_env()

fs_tool_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            WORKSPACE_PATH,
        ],
        env={}
    ))