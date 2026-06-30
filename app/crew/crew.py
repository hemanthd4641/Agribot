"""CrewAI Orchestrator."""

import json
import logging
from crewai import Crew, Process
from langchain_groq import ChatGroq
from app.crew.agents import create_agents
from app.crew.tasks import create_tasks
from flask import current_app

logger = logging.getLogger(__name__)

class AgriCrew:
    """Manages the execution of the agricultural multi-agent system."""

    def __init__(self, session_id: str, groq_api_key: str):
        self.session_id = session_id
        
        # We reuse the existing Groq API key to power the Langchain LLM for CrewAI
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile", # Or whichever model is configured
            api_key=groq_api_key
        )
        
        self.agents = create_agents(self.llm)

    def _task_callback(self, task_output):
        """Callback fired when a task completes. Updates Redis for frontend SSE/polling."""
        try:
            # We must be in app context here if called synchronously
            memory_service = current_app.memory_service
            
            # CrewAI TaskOutput object has description, expected_output, raw, agent
            # Try to extract agent role to update status
            agent_role = getattr(task_output.agent, 'role', 'Coordinator') if hasattr(task_output, 'agent') else 'Unknown Agent'
            
            # Read current status list
            status_key = f"crew_status:{self.session_id}"
            current_status = memory_service.redis_client.get(status_key) if memory_service.redis_client else None
            
            status_list = json.loads(current_status) if current_status else []
            status_list.append({
                "agent": agent_role,
                "status": "completed"
            })
            
            if memory_service.redis_client:
                memory_service.redis_client.setex(status_key, 3600, json.dumps(status_list))
                
        except Exception as e:
            logger.error("Task callback error: %s", e)


    def kickoff(self, user_query: str) -> str:
        """Execute the CrewAI flow for a given query."""
        logger.info("Starting AgriCrew execution for session: %s", self.session_id)
        
        # Reset status
        memory_service = current_app.memory_service
        if memory_service.redis_client:
            status_key = f"crew_status:{self.session_id}"
            memory_service.redis_client.setex(status_key, 3600, json.dumps([]))
            
        tasks = create_tasks(self.agents, user_query)
        
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
            task_callback=self._task_callback
        )
        
        # Execute the crew
        # CrewAI's kickoff returns a CrewOutput object. The final string is typically in raw
        result = crew.kickoff()
        
        if hasattr(result, 'raw'):
            return result.raw
        return str(result)
