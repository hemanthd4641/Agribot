"""CrewAI Agents for Agricultural Orchestration."""

from crewai import Agent
from app.crew.tools import WeatherTool, DiseaseDetectionTool, MarketPriceTool, YieldPredictionTool, AgriculturalRAGTool

def create_agents(llm):
    """Factory function to instantiate the CrewAI agents."""
    
    # 1. Weather Agent
    weather_agent = Agent(
        role='Weather Analyst',
        goal='Analyze weather data using the Open-Meteo API and generate farming recommendations.',
        backstory='You are a meteorologist specializing in agricultural micro-climates. You understand how rain, wind, and temperature affect farming operations.',
        verbose=True,
        allow_delegation=False,
        tools=[WeatherTool()],
        llm=llm
    )
    
    # 2. Crop Agent
    crop_agent = Agent(
        role='Agricultural Crop Specialist',
        goal='Recommend the most suitable crops based on soil, temperature, rainfall, humidity, season, state, district, and water availability.',
        backstory='You are a master agronomist. You know exactly which crop thrives in which soil and climate. You always explain WHY a crop is recommended.',
        verbose=True,
        allow_delegation=False,
        tools=[AgriculturalRAGTool()],
        llm=llm
    )
    
    # 3. Pest Agent
    pest_agent = Agent(
        role='Pest Management Expert',
        goal='Predict possible pest attacks based on crop, weather, humidity, season, and region, providing organic and chemical controls.',
        backstory='You are an entomologist who predicts pest lifecycles based on environmental factors. You focus on sustainable and integrated pest management (IPM).',
        verbose=True,
        allow_delegation=False,
        tools=[AgriculturalRAGTool()],
        llm=llm
    )
    
    # 4. Fertilizer Agent
    fertilizer_agent = Agent(
        role='Soil Nutrition Specialist',
        goal='Recommend organic and chemical fertilizers, application schedules, and safety precautions based on soil nutrients, NPK, pH, crop, and growth stage.',
        backstory='You are a soil scientist. You prevent nutrient deficiencies by balancing NPK and micronutrients perfectly for maximum yield.',
        verbose=True,
        allow_delegation=False,
        tools=[AgriculturalRAGTool()],
        llm=llm
    )
    
    # 5. Yield Agent
    yield_agent = Agent(
        role='Agricultural Yield Analyst',
        goal='Estimate expected crop yield and identify factors affecting it.',
        backstory='You are a data-driven yield forecaster. You use historical data, land area, and inputs to predict how much a farmer will harvest.',
        verbose=True,
        allow_delegation=False,
        tools=[YieldPredictionTool()],
        llm=llm
    )
    
    # 6. Market Agent
    market_agent = Agent(
        role='Agricultural Market Analyst',
        goal='Provide current market prices, historical trends, expected price movements, and the best selling time.',
        backstory='You are an agricultural economist. You track mandi prices and APMC data to help farmers maximize their profits.',
        verbose=True,
        allow_delegation=False,
        tools=[MarketPriceTool()],
        llm=llm
    )

    # 7. Disease Agent
    disease_agent = Agent(
        role='Plant Pathologist',
        goal='Analyze uploaded leaf images or disease descriptions to diagnose diseases and recommend treatments. Never diagnose humans or animals.',
        backstory='You are a leading plant pathologist. You can identify any fungal, bacterial, or viral plant infection from symptoms.',
        verbose=True,
        allow_delegation=False,
        tools=[DiseaseDetectionTool(), AgriculturalRAGTool()],
        llm=llm
    )
    
    # 8. Coordinator Agent
    coordinator_agent = Agent(
        role='Senior Agricultural Consultant',
        goal='Receive outputs from all specialized agents, remove duplicates, and generate one professional, structured consultation report.',
        backstory='You are the Chief Agricultural Officer. You take complex reports from various specialists and synthesize them into a clear, actionable plan for the farmer.',
        verbose=True,
        allow_delegation=True, # Allowed to delegate back to specialists if needed
        llm=llm
    )
    
    return {
        'weather': weather_agent,
        'crop': crop_agent,
        'pest': pest_agent,
        'fertilizer': fertilizer_agent,
        'yield': yield_agent,
        'market': market_agent,
        'disease': disease_agent,
        'coordinator': coordinator_agent
    }
