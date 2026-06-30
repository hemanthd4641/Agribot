"""CrewAI Tasks for Agricultural Orchestration."""

from crewai import Task

def create_tasks(agents, query: str, active_flags: dict = None):
    """Factory function to instantiate the tasks based on user query and intent routing."""
    
    if active_flags is None:
        active_flags = {
            "weather": True, "crop": True, "disease": True, 
            "pest": True, "fertilizer": True, "yield_prediction": True, "market": True
        }
        
    tasks = []
    created_tasks = {}
    
    # Task 1: Weather
    if active_flags.get('weather', True):
        weather_task = Task(
            description=f"Analyze the following user query to determine the location and fetch current weather and forecasts. Extract any agricultural weather implications. Query: '{query}'",
            expected_output="A summary of the current weather, 7-day forecast, and immediate weather-related farming advice.",
            agent=agents['weather']
        )
        tasks.append(weather_task)
        created_tasks['weather'] = weather_task
    
    # Task 2: Crop
    if active_flags.get('crop', True):
        crop_context = []
        if 'weather' in created_tasks:
            crop_context.append(created_tasks['weather'])
            
        crop_task = Task(
            description=f"Based on the weather data (if any) and the user's query, recommend suitable crops or analyze the user's current crop. Explain WHY. Query: '{query}'",
            expected_output="A list of recommended crops with reasoning based on soil, climate, and water availability, or advice on the user's specific crop.",
            agent=agents['crop'],
            context=crop_context if crop_context else None
        )
        tasks.append(crop_task)
        created_tasks['crop'] = crop_task
    
    # Task 3: Disease
    if active_flags.get('disease', True):
        disease_task = Task(
            description=f"Check if the user's query mentions any plant disease symptoms or includes an image description. If so, diagnose it. Query: '{query}'",
            expected_output="A diagnosis of the plant disease (if any), confidence level, symptoms, and organic/chemical treatments. If no disease is mentioned, output 'No disease symptoms reported.'",
            agent=agents['disease']
        )
        tasks.append(disease_task)
        created_tasks['disease'] = disease_task

    # Task 4: Pest
    if active_flags.get('pest', True):
        pest_context = []
        for key in ['weather', 'crop', 'disease']:
            if key in created_tasks:
                pest_context.append(created_tasks[key])
                
        pest_task = Task(
            description=f"Predict likely pest attacks for the crops identified, factoring in the weather forecast and region. Provide control measures. Query: '{query}'",
            expected_output="Predicted pests, risk levels, symptoms, and organic/chemical control measures.",
            agent=agents['pest'],
            context=pest_context if pest_context else None
        )
        tasks.append(pest_task)
        created_tasks['pest'] = pest_task
    
    # Task 5: Fertilizer
    if active_flags.get('fertilizer', True):
        fert_context = []
        for key in ['weather', 'crop']:
            if key in created_tasks:
                fert_context.append(created_tasks[key])
                
        fertilizer_task = Task(
            description=f"Recommend a fertilizer schedule for the identified crops, considering the weather (e.g., don't fertilize before heavy rain). Query: '{query}'",
            expected_output="Organic and chemical fertilizer recommendations, application schedules, and safety precautions.",
            agent=agents['fertilizer'],
            context=fert_context if fert_context else None
        )
        tasks.append(fertilizer_task)
        created_tasks['fertilizer'] = fertilizer_task
    
    # Task 6: Yield
    if active_flags.get('yield_prediction', True):
        yield_context = []
        for key in ['crop', 'fertilizer']:
            if key in created_tasks:
                yield_context.append(created_tasks[key])
                
        yield_task = Task(
            description=f"If the user provided land area, predict the yield for the crop. Otherwise, provide general yield expectations per acre. Query: '{query}'",
            expected_output="Expected yield, confidence, factors affecting yield, and improvement suggestions.",
            agent=agents['yield'],
            context=yield_context if yield_context else None
        )
        tasks.append(yield_task)
        created_tasks['yield'] = yield_task
    
    # Task 7: Market
    if active_flags.get('market', True):
        market_context = []
        for key in ['crop', 'yield']:
            if key in created_tasks:
                market_context.append(created_tasks[key])
                
        market_task = Task(
            description=f"Analyze the market price and trends for the identified crop in the user's region. Query: '{query}'",
            expected_output="Current market price, nearby market locations, historical trends, expected price movements, and best selling time.",
            agent=agents['market'],
            context=market_context if market_context else None
        )
        tasks.append(market_task)
        created_tasks['market'] = market_task
    
    # Task 8: Coordination (Final Report) - ALWAYS RUNS
    coordinator_task = Task(
        description=(
            f"Review the outputs from the specialized agents that were invoked. "
            f"Merge them into a single, highly professional structured consultation report for the user's original query: '{query}'. "
            f"Only include sections for the information provided by the agents. If an agent wasn't needed, omit its section. "
            f"The final report must be in Markdown."
        ),
        expected_output="A complete, perfectly formatted Markdown report synthesizing all specialized agent advice provided.",
        agent=agents['coordinator'],
        context=tasks.copy() if tasks else None
    )
    
    tasks.append(coordinator_task)
    
    return tasks
