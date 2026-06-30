"""CrewAI Tasks for Agricultural Orchestration."""

from crewai import Task

def create_tasks(agents, query: str):
    """Factory function to instantiate all possible CrewAI tasks.
    We will selectively filter these down during orchestration."""
    
    # 1. Weather Task
    weather_task = Task(
        description=f"Fetch the current weather and 7-day forecast for the location mentioned in this query: '{query}'. If no location is mentioned, ask the user or default to the user's inferred region. Do not continue reasoning after a valid answer is available.",
        expected_output="A summary of the current weather and forecast, including temperature, humidity, and rainfall.",
        agent=agents['weather']
    )
    
    # 2. Crop Task
    crop_task = Task(
        description=f"Recommend the top crops based on the supplied soil, weather, and region data in this query: '{query}'. Fetch weather data if necessary. Do not continue reasoning after a valid answer is available.",
        expected_output="A list of recommended crops and reasons for their suitability.",
        agent=agents['crop']
    )
    
    # 3. Pest Task
    pest_task = Task(
        description=f"Identify potential pest threats and recommend specific IPM strategies for the crops mentioned in this query: '{query}'. Fetch weather data if necessary. Do not continue reasoning after a valid answer is available.",
        expected_output="A list of potential pests and organic/chemical control measures.",
        agent=agents['pest']
    )
    
    # 4. Fertilizer Task
    fertilizer_task = Task(
        description=f"Recommend a specific fertilizer schedule and nutrient management plan for the crop mentioned in this query: '{query}'. Fetch weather data if necessary. Do not continue reasoning after a valid answer is available.",
        expected_output="A detailed fertilizer schedule and nutrient management plan.",
        agent=agents['fertilizer']
    )
    
    # 5. Yield Task
    yield_task = Task(
        description=f"Predict the expected yield range based on the crop, area, and region mentioned in this query: '{query}'. Fetch weather data if necessary. Do not continue reasoning after a valid answer is available.",
        expected_output="An estimated yield range in quintals or tons, with a confidence score.",
        agent=agents['yield']
    )
    
    # 6. Market Task
    market_task = Task(
        description=f"Get the current market price and 2-week forecast for the crop mentioned in this query: '{query}'. Do not continue reasoning after a valid answer is available.",
        expected_output="Current market price, expected trends, and selling advice.",
        agent=agents['market']
    )
    
    # 7. Disease Task
    disease_task = Task(
        description=f"Identify the plant disease based on the symptoms described in this query: '{query}'. Recommend treatments. Fetch weather data if necessary. Do not continue reasoning after a valid answer is available.",
        expected_output="Diagnosis of the disease and a step-by-step treatment plan.",
        agent=agents['disease']
    )
    
    # 8. Coordinator Task (Always executed last)
    coordinator_task = Task(
        description=f"Collect outputs from all executed agents regarding this query: '{query}'. Merge responses. Do not re-invoke other agents. Do not continue reasoning after a valid answer is available.",
        expected_output="A cohesive, farmer-friendly Markdown report containing all insights.",
        agent=agents['coordinator']
    )
    
    return {
        'weather': weather_task,
        'crop': crop_task,
        'pest': pest_task,
        'fertilizer': fertilizer_task,
        'yield': yield_task,
        'market': market_task,
        'disease': disease_task,
        'coordinator': coordinator_task
    }
