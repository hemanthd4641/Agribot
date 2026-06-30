"""CrewAI Orchestrator - Hybrid Architecture.

Executes a subset of specialized agents based on the detected intent.
"""

import json
import logging
import time
from crewai import Crew, Process
from langchain_groq import ChatGroq
from app.crew.agents import create_agents
from app.crew.tasks import create_tasks
from flask import current_app

logger = logging.getLogger(__name__)

class AgriCrew:
    """Manages the execution of the dynamic CrewAI pipeline."""

    # We reuse the LLM and Agents across requests as requested ("Reuse LLM, Agents")
    _shared_llm = None
    _shared_agents = None

    def __init__(self, session_id: str, groq_api_key: str):
        self.session_id = session_id
        
        if AgriCrew._shared_llm is None:
            AgriCrew._shared_llm = ChatGroq(
                temperature=0.7,
                model_name="llama-3.3-70b-versatile",
                api_key=groq_api_key
            )
            AgriCrew._shared_agents = create_agents(AgriCrew._shared_llm)

    def _push_ui_status(self, agent_name: str):
        """Manually push status updates to Redis for the UI."""
        memory_service = current_app.memory_service
        if memory_service and memory_service.client:
            status_key = f"crew_status:{self.session_id}"
            current_status = memory_service.client.get(status_key)
            status_list = []
            if current_status:
                try:
                    status_list = json.loads(current_status)
                except json.JSONDecodeError:
                    pass
            status_list.append({"agent": agent_name, "status": "completed"})
            memory_service.client.setex(status_key, 3600, json.dumps(status_list))

    def kickoff(self, user_query: str, intent: str) -> str:
        """Execute the CrewAI pipeline dynamically based on intent."""
        start_exec_time = time.time()
        logger.info("Starting CrewAI execution for intent: %s (session: %s)", intent, self.session_id)
        
        # Reset UI Status
        memory_service = current_app.memory_service
        if memory_service and memory_service.client:
            status_key = f"crew_status:{self.session_id}"
            memory_service.client.setex(status_key, 3600, json.dumps([]))

        # Generate fresh tasks for this specific query
        all_tasks = create_tasks(AgriCrew._shared_agents, user_query)
        
        # Select active tasks based on intent
        active_agents = []
        active_tasks = []
        
        def add_task(key: str):
            if key not in [a.role for a in active_agents]:
                active_agents.append(AgriCrew._shared_agents[key])
                active_tasks.append(all_tasks[key])

        # Routing Logic
        if intent == "WEATHER":
            add_task('weather')
        elif intent == "CROP_RECOMMENDATION":
            add_task('crop')
        elif intent == "DISEASE_DETECTION":
            add_task('disease')
        elif intent == "YIELD_PREDICTION":
            add_task('yield')
        elif intent == "FERTILIZER_RECOMMENDATION":
            add_task('fertilizer')
        elif intent == "PEST_PREDICTION":
            add_task('pest')
        elif intent == "MARKET_PRICE":
            add_task('market')
        else:
            add_task('crop') # Fallback
            
        # Always add coordinator
        add_task('coordinator')
            
        logger.info("Selected Agent for %s: %s", intent, [a.role for a in active_agents])
        
        for agent in active_agents:
            self._push_ui_status(agent.role)

        logger.info(f"DEBUG: Detected intent = {intent}")
        logger.info(f"DEBUG: Selected agents = {[a.role for a in active_agents]}")
        logger.info(f"DEBUG: Selected tasks = {[t.description for t in active_tasks]}")
        
        crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=False,
            memory=False # Reduce token usage
        )
        
        try:
            logger.info("DEBUG: Crew kickoff started")
            result = crew.kickoff()
            final_report = result.raw if hasattr(result, 'raw') else str(result)
            logger.info("DEBUG: Crew kickoff completed successfully")
        except Exception as e:
            import traceback
            print("====================================")
            print("CREW FAILURE DETECTED")
            print("====================================")
            print(f"Exception type: {type(e).__name__}")
            print("Full stack trace:")
            traceback.print_exc()
            print("====================================")
            logger.error("CrewAI execution failed: %s", e)
            raise e # Let chat.py catch this and fallback to standard LLM
        
        total_time = time.time() - start_exec_time
        logger.info(f"CrewAI execution completed in {total_time:.2f}s.")
        self._push_ui_status("Final Report Ready")
        
        return final_report
