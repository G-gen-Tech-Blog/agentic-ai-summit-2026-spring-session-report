from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from . import tools
from .config import Config

config = Config()

root_agent = Agent(
    name="calendar_agent",
    model=LiteLlm(
        config.model_id,
        vertex_location=config.vertex_location,
    ),
    description=config.description,
    instruction=config.instruction,
    tools=[
        tools.read_todo_file,
        tools.create_calendar_event,
        tools.list_calendar_events,
        tools.update_calendar_event,
        tools.delete_calendar_event,
    ],
)
