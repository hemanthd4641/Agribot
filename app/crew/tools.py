"""CrewAI Custom Tools for Agricultural Agents."""

import logging
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from flask import current_app

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
#  Schemas
# --------------------------------------------------------------------------- #

class WeatherInput(BaseModel):
    """Input schema for Weather Tool."""
    location: str = Field(..., description="The city, district, or region to get the weather for.")

class ImageAnalysisInput(BaseModel):
    """Input schema for Image Analysis/Disease Detection Tool."""
    image_description: str = Field(..., description="A description of the image provided by the user, or symptoms they mentioned.")

class MarketInput(BaseModel):
    """Input schema for Market Price Tool."""
    crop: str = Field(..., description="The crop name.")
    region: str = Field(..., description="The region, state, or district.")

class YieldInput(BaseModel):
    """Input schema for Yield Prediction Tool."""
    crop: str = Field(..., description="The crop being grown.")
    area_acres: float = Field(..., description="The land area in acres.")
    region: str = Field(..., description="The region or soil type.")

class RagInput(BaseModel):
    """Input schema for RAG Document Tool."""
    query: str = Field(..., description="The agricultural query to search in the knowledge base.")


# --------------------------------------------------------------------------- #
#  Tools
# --------------------------------------------------------------------------- #

class WeatherTool(BaseTool):
    name: str = "Weather Intelligence Tool"
    description: str = "Gets current weather, 7-day forecast, and agricultural weather advice for a location."
    args_schema: type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        try:
            # We must be inside an app context to use current_app
            weather_service = current_app.weather_service
            coords = weather_service.get_coordinates(location)
            if not coords:
                return f"Could not find coordinates for location: {location}"
            
            weather_data = weather_service.get_weather_data(coords['lat'], coords['lon'])
            if not weather_data:
                return f"Could not fetch weather data for {location}"
                
            return (
                f"Weather for {location}:\n"
                f"Current Temp: {weather_data['current'].get('temperature_2m')}°C\n"
                f"Humidity: {weather_data['current'].get('relative_humidity_2m')}%\n"
                f"Rain expected today: {weather_data['daily'].get('precipitation_probability_max', [0])[0]}%\n"
            )
        except Exception as e:
            logger.error("WeatherTool error: %s", e)
            return f"Error fetching weather: {str(e)}"


class DiseaseDetectionTool(BaseTool):
    name: str = "Disease Detection & Vision Tool"
    description: str = "Analyzes a described plant image or symptoms to detect diseases and recommend treatments."
    args_schema: type[BaseModel] = ImageAnalysisInput

    def _run(self, image_description: str) -> str:
        # Mock implementation using LLM reasoning since actual image isn't passed here natively 
        # (CrewAI can handle image paths if we build a custom vision tool, but we will mock it based on description)
        return (
            f"Based on the visual symptoms described ({image_description}), the plant likely suffers from a fungal infection "
            f"or nutrient deficiency. Recommend checking for leaf spots, applying a broad-spectrum organic fungicide like Neem oil, "
            f"and ensuring proper drainage."
        )


class MarketPriceTool(BaseTool):
    name: str = "Market Price Tool"
    description: str = "Fetches current agricultural market prices, historical trends, and selling advice for a crop in a specific region."
    args_schema: type[BaseModel] = MarketInput

    def _run(self, crop: str, region: str) -> str:
        # Mock API integration
        return (
            f"Market Analysis for {crop} in {region}:\n"
            f"- Current Avg Price: ₹2,400 per quintal.\n"
            f"- Trend: Prices are expected to rise by 5% in the next two weeks due to seasonal demand.\n"
            f"- Recommendation: Hold stock for 1 week if storage permits, or sell in the nearby APMC market."
        )


class YieldPredictionTool(BaseTool):
    name: str = "Yield Prediction Tool"
    description: str = "Estimates expected crop yield based on crop type, area, and region."
    args_schema: type[BaseModel] = YieldInput

    def _run(self, crop: str, area_acres: float, region: str) -> str:
        # Mock ML Model
        base_yield = 15 # quintals per acre (arbitrary baseline)
        estimated_yield = base_yield * area_acres
        return (
            f"Yield Prediction for {area_acres} acres of {crop} in {region}:\n"
            f"- Estimated Yield: {estimated_yield} to {estimated_yield * 1.2} quintals.\n"
            f"- Confidence: 85%\n"
            f"- Factors: Soil quality and upcoming weather patterns are favorable. Ensure timely fertilizer application."
        )


class AgriculturalRAGTool(BaseTool):
    name: str = "Agricultural Knowledge Base (RAG)"
    description: str = "Searches specialized agricultural documents, government schemes, and research papers."
    args_schema: type[BaseModel] = RagInput

    def _run(self, query: str) -> str:
        # Mock RAG retrieval
        return (
            f"Knowledge Base Retrieval for '{query}':\n"
            f"According to the latest agricultural guidelines, ensure you follow integrated pest management (IPM) practices "
            f"and utilize available subsidies under the PM-KISAN or PMFBY schemes if applicable to this query."
        )
