"""Test script for Hybrid Architecture."""

import os
import sys
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.services.intent_router import IntentRouter
from app.crew.crew import AgriCrew

def main():
    app = create_app()
    with app.app_context():
        # Test Intent Router
        router = IntentRouter()
        
        queries = [
            "What is crop rotation?",
            "What is the weather in Bangalore today?",
            "Can you predict the yield for 10 acres of rice in Punjab?",
        ]
        
        print("=== Testing Intent Router ===")
        for q in queries:
            intent = router.classify_intent(q)
            print(f"Query: '{q}' -> Intent: {intent}")
            
        print("\n=== Testing CrewAI Dynamic Orchestration ===")
        # Force a weather query
        crew = AgriCrew(session_id="test_session_123", groq_api_key=app.config['GROQ_API_KEY'])
        try:
            print("Executing Weather Intent...")
            res = crew.kickoff("What is the weather in Bangalore today?", intent="WEATHER")
            print("SUCCESS! Output length:", len(res))
            print(res[:200] + "...")
        except Exception as e:
            print(f"EXPECTED FAILURE OR RATE LIMIT: {e}")

if __name__ == "__main__":
    main()
