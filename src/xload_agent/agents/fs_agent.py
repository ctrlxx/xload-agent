from veadk import Agent
from google.adk.artifacts import InMemoryArtifactService
from veadk.memory.short_term_memory import ShortTermMemory
from xload_agent.tools.fs.grep import grep_tool
from xload_agent.tools.fs.ls import ls_tool
from xload_agent.tools.fs.tree import tree_tool
from xload_agent.prompts import apply_prompt_template
from xload_agent.config import Config

config = Config()
WORKSPACE_PATH = config.workspace_path

# 创建文件系统agent
fs_agent = Agent(
    name="fs_agent",
    description="一个专门处理文件系统操作的代理，提供文件浏览、搜索和目录结构查看功能",
    instruction=apply_prompt_template("fs_agent", PROJECT_ROOT=WORKSPACE_PATH),
    tools=[grep_tool, ls_tool, tree_tool],
    artifact_service=InMemoryArtifactService(),
    memory_service=ShortTermMemory()
)

__all__ = ["fs_agent"]