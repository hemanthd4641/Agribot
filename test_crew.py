import os
from flask import Flask
from app.config import AppConfig
from app.crew.crew import AgriCrew

app = Flask(__name__)
app.config.from_object(AppConfig)

# Mock memory service
class MockMemory:
    client = None

app.memory_service = MockMemory()

with app.app_context():
    try:
        crew = AgriCrew(session_id="test", groq_api_key=AppConfig.GROQ_API_KEY)
        print("Crew initialized successfully.")
        res = crew.kickoff("What is the weather tomorrow in Bengaluru for my tomato crop?")
        print("Crew kickoff finished.")
        print(res)
    except Exception as e:
        import traceback
        traceback.print_exc()
