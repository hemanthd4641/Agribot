"""CrewAI Tasks for Agricultural Orchestration."""

from crewai import Task

def create_tasks(agents, query: str):
    """Factory function to instantiate the tasks based on user query."""
    
    # Task 1: Weather
    weather_task = Task(
        description=f"Analyze the following user query to determine the location and fetch current weather and forecasts. Extract any agricultural weather implications. Query: '{query}'",
        expected_output="A summary of the current weather, 7-day forecast, and immediate weather-related farming advice.",
        agent=agents['weather']
    )
    
    # Task 2: Crop
    crop_task = Task(
        description=f"Based on the weather data and the user's query, recommend suitable crops or analyze the user's current crop. Explain WHY. Query: '{query}'",
        expected_output="A list of recommended crops with reasoning based on soil, climate, and water availability, or advice on the user's specific crop.",
        agent=agents['crop'],
        context=[weather_task]
    )
    
    # Task 3: Disease
    disease_task = Task(
        description=f"Check if the user's query mentions any plant disease symptoms or includes an image description. If so, diagnose it. Query: '{query}'",
        expected_output="A diagnosis of the plant disease (if any), confidence level, symptoms, and organic/chemical treatments. If no disease is mentioned, output 'No disease symptoms reported.'",
        agent=agents['disease']
    )

    # Task 4: Pest
    pest_task = Task(
        description=f"Predict likely pest attacks for the crops identified, factoring in the weather forecast and region. Provide control measures.",
        expected_output="Predicted pests, risk levels, symptoms, and organic/chemical control measures.",
        agent=agents['pest'],
        context=[weather_task, crop_task, disease_task]
    )
    
    # Task 5: Fertilizer
    fertilizer_task = Task(
        description=f"Recommend a fertilizer schedule for the identified crops, considering the weather (e.g., don't fertilize before heavy rain).",
        expected_output="Organic and chemical fertilizer recommendations, application schedules, and safety precautions.",
        agent=agents['fertilizer'],
        context=[weather_task, crop_task]
    )
    
    # Task 6: Yield
    yield_task = Task(
        description=f"If the user provided land area, predict the yield for the crop. Otherwise, provide general yield expectations per acre.",
        expected_output="Expected yield, confidence, factors affecting yield, and improvement suggestions.",
        agent=agents['yield'],
        context=[crop_task, fertilizer_task]
    )
    
    # Task 7: Market
    market_task = Task(
        description=f"Analyze the market price and trends for the identified crop in the user's region.",
        expected_output="Current market price, nearby market locations, historical trends, expected price movements, and best selling time.",
        agent=agents['market'],
        context=[crop_task, yield_task]
    )
    
    # Task 8: Coordination (Final Report)
    coordinator_task = Task(
        description=(
            f"Review the outputs from the Weather, Crop, Disease, Pest, Fertilizer, Yield, and Market agents. "
            f"Merge them into a single, highly professional structured consultation report for the user's original query: '{query}'. "
            f"Remove any duplicate information. If an agent reported 'Not applicable' or 'Data unavailable', handle it gracefully without failing. "
            f"The final report must strictly follow this Markdown structure:\n"
            f"## Weather Summary\n"
            f"## Crop Recommendation\n"
            f"## Disease Analysis (if applicable)\n"
            f"## Pest Prediction\n"
            f"## Fertilizer Plan\n"
            f"## Yield Prediction\n"
            f"## Market Analysis\n"
            f"## Action Plan"
        ),
        expected_output="A complete, perfectly formatted Markdown report synthesizing all specialized agent advice.",
        agent=agents['coordinator'],
        context=[weather_task, crop_task, disease_task, pest_task, fertilizer_task, yield_task, market_task]
    )
    
    return [
        weather_task,
        crop_task,
        disease_task,
        pest_task,
        fertilizer_task,
        yield_task,
        market_task,
        coordinator_task
    ]
