"""Weather Service for AgriIntel AI Assistant.

Integrates with the Open-Meteo free API to fetch geocoding data,
current weather, and 7-day forecasts for agricultural recommendations.
Includes a simple in-memory cache with a 15-minute TTL.
"""

import logging
import time
from typing import Dict, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for handling Open-Meteo API requests and caching."""

    def __init__(self) -> None:
        """Initialize the Weather Service with an empty cache."""
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl: int = 900  # 15 minutes in seconds
        logger.info("Weather Service initialized with 15m in-memory cache.")

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Retrieve a valid item from the cache if it hasn't expired."""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.cache_ttl:
                logger.debug("Cache hit for %s", key)
                return entry['data']
            else:
                logger.debug("Cache expired for %s", key)
                del self.cache[key]
        return None

    def _save_to_cache(self, key: str, data: Dict) -> None:
        """Save an item to the cache with the current timestamp."""
        self.cache[key] = {
            'timestamp': time.time(),
            'data': data
        }

    def get_location_coordinates(self, city_name: str) -> Optional[Tuple[float, float, str]]:
        """Fetch latitude, longitude, and proper name for a given city.
        
        Args:
            city_name: The name of the city to search for.
            
        Returns:
            Tuple of (latitude, longitude, formatted_name) or None if not found.
        """
        cache_key = f"geo_{city_name.lower()}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached['lat'], cached['lon'], cached['name']

        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city_name,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results")
            if not results:
                return None
                
            location = results[0]
            lat = location.get("latitude")
            lon = location.get("longitude")
            
            # Format name nicely (e.g., "Bangalore, India")
            name = location.get("name")
            if location.get("country"):
                name = f"{name}, {location.get('country')}"
                
            self._save_to_cache(cache_key, {'lat': lat, 'lon': lon, 'name': name})
            return lat, lon, name
            
        except requests.RequestException as e:
            logger.error("Geocoding API error for %s: %s", city_name, e)
            return None

    def get_weather_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Fetch current weather and 7-day forecast from Open-Meteo.
        
        Args:
            lat: Latitude.
            lon: Longitude.
            
        Returns:
            Dictionary containing 'current' and 'daily' weather data, or None on error.
        """
        # Round coords slightly to improve cache hit rate for nearby points
        cache_key = f"weather_{round(lat, 3)}_{round(lon, 3)}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max,precipitation_sum,rain_sum,precipitation_probability_max,wind_speed_10m_max",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self._save_to_cache(cache_key, data)
            return data
            
        except requests.RequestException as e:
            logger.error("Forecast API error for %s,%s: %s", lat, lon, e)
            return None

    def get_weather_for_city(self, city_name: str) -> Dict:
        """High-level function to get all weather info for a city.
        
        Returns:
            Dict containing status, location details, and weather data.
        """
        location = self.get_location_coordinates(city_name)
        if not location:
            return {"status": "error", "message": f"Could not find location: {city_name}"}
            
        lat, lon, name = location
        weather = self.get_weather_data(lat, lon)
        
        if not weather:
            return {"status": "error", "message": f"Could not fetch weather for {name}"}
            
        return {
            "status": "success",
            "location": {
                "name": name,
                "latitude": lat,
                "longitude": lon
            },
            "weather": weather
        }
