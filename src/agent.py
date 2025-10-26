from veadk import Agent, Runner
from veadk.memory.short_term_memory import ShortTermMemory

from google.adk.artifacts import InMemoryArtifactService

from xload_agent.prompts import apply_prompt_template
from xload_agent.agents.terminal_agent import terminal_agent
from xload_agent.agents.k6_agent import k6_agent

from xload_agent.tools import fs_tool_mcp

from xload_agent.config import Config

config = Config()

app_name = "xload_agent_app"
user_id = "xload_agent_user"
session_id = "xload_agent_session"

artifact_service = InMemoryArtifactService()
short_term_memory = ShortTermMemory()

root_agent = Agent( 
    name="xload_agent",
    description=("An agent that can help you create and run k6 scripts"),
    instruction=apply_prompt_template("root_agent", PROJECT_ROOT=config.workspace_path),
    tools=[fs_tool_mcp],
    sub_agents=[terminal_agent, k6_agent],
    artifact_service=artifact_service,
    memory_service=short_term_memory
)


runner = Runner(
    agent=root_agent, short_term_memory=short_term_memory, app_name=app_name, user_id=user_id
)

async def main(messages: str):
    response = await runner.run(
        messages=messages,
        session_id=session_id
    )
    print(f"prompt: {messages}, response: {response}")

if __name__ == "__main__":
    import asyncio
    k6_script_prompt = "请生成一个k6脚本，模拟100个用户并发访问一个接口，每个用户访问10次"
    prompt = k6_script_prompt
    asyncio.run(main(prompt))