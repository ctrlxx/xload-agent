from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from src.agent import root_agent


# Create ADK middleware agent instance
adk_agent_sample = ADKAgent(
    adk_agent=root_agent,
    app_name="xload",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Create FastAPI app
app = FastAPI(title="XLoad Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_agent_sample, path="/")

# If you want the server to run on invocation, you can do the following:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)