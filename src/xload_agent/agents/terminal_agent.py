from veadk import Agent
from google.adk.artifacts import InMemoryArtifactService
from veadk.memory.short_term_memory import ShortTermMemory
from xload_agent.tools.terminal.bash import bash_tool
from xload_agent.prompts import apply_prompt_template
from xload_agent.config import Config

config = Config()
WORKSPACE_PATH = config.workspace_path


# 创建终端操作agent
terminal_agent = Agent(
    name="terminal_agent",
    description="一个专门处理终端命令执行的代理，提供bash命令运行功能",
    instruction=apply_prompt_template("terminal_agent", PROJECT_ROOT=WORKSPACE_PATH),
    tools=[bash_tool],
    artifact_service=InMemoryArtifactService(),
    memory_service=ShortTermMemory()
)

__all__ = ["terminal_agent"]