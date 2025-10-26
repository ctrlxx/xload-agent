from veadk import Agent
from google.adk.artifacts import InMemoryArtifactService
from veadk.memory.short_term_memory import ShortTermMemory
from xload_agent.tools.k6.run import k6_tool
from xload_agent.prompts import apply_prompt_template
from xload_agent.config import Config

config = Config()
WORKSPACE_PATH = config.workspace_path

# 创建k6脚本执行agent
k6_agent = Agent(
    name="k6_agent",
    description="一个专门处理k6脚本执行的代理，提供k6脚本运行和负载测试功能",
    instruction=apply_prompt_template("k6_agent", PROJECT_ROOT=WORKSPACE_PATH),
    tools=[k6_tool],
    artifact_service=InMemoryArtifactService(),
    memory_service=ShortTermMemory()
)

__all__ = ["k6_agent"]