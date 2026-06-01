import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional

WEATHER_CACHE = "weather_cache.json"
OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

class WeatherManager:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize weather manager with API key"""
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY environment variable not set")
    
    def get_weather_by_city(self, city: str) -> Dict:
        """Fetch current weather for a city"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(OPENWEATHER_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            self._cache_weather(city, data)
            return self._format_weather(data)
        except requests.exceptions.RequestException as e:
            print(f"[WEATHER] Error fetching weather: {e}")
            return self._load_cached_weather(city)
    
    def get_weather_by_coords(self, lat: float, lon: float) -> Dict:
        """Fetch current weather by latitude/longitude"""
        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(OPENWEATHER_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            city = data.get("name", "Unknown")
            self._cache_weather(city, data)
            return self._format_weather(data)
        except requests.exceptions.RequestException as e:
            print(f"[WEATHER] Error fetching weather: {e}")
            return None
    
    def get_forecast(self, city: str, days: int = 5) -> Dict:
        """Fetch weather forecast (5-day)"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
            }
            response = requests.get(FORECAST_API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return self._format_forecast(data)
        except requests.exceptions.RequestException as e:
            print(f"[WEATHER] Error fetching forecast: {e}")
            return None
    
    @staticmethod
    def _format_weather(data: Dict) -> Dict:
        """Format API response for display"""
        return {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temp": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "description": data.get("weather", [{}])[0].get("description", "").title(),
            "icon": data.get("weather", [{}])[0].get("icon"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "wind_deg": data.get("wind", {}).get("deg"),
            "clouds": data.get("clouds", {}).get("all"),
            "sunrise": data.get("sys", {}).get("sunrise"),
            "sunset": data.get("sys", {}).get("sunset"),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _format_forecast(data: Dict) -> Dict:
        """Format forecast API response"""
        forecasts = []
        for item in data.get("list", []):
            forecasts.append({
                "time": item.get("dt_txt"),
                "temp": item.get("main", {}).get("temp"),
                "description": item.get("weather", [{}])[0].get("description", "").title(),
                "icon": item.get("weather", [{}])[0].get("icon"),
                "humidity": item.get("main", {}).get("humidity"),
                "wind_speed": item.get("wind", {}).get("speed"),
                "rain": item.get("rain", {}).get("3h", 0)
            })
        return {
            "city": data.get("city", {}).get("name"),
            "country": data.get("city", {}).get("country"),
            "forecast": forecasts
        }
    
    @staticmethod
    def _cache_weather(city: str, data: Dict):
        """Cache weather data locally"""
        try:
            cache = {}
            if os.path.exists(WEATHER_CACHE):
                with open(WEATHER_CACHE, "r") as f:
                    cache = json.load(f)
            
            cache[city] = {
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(WEATHER_CACHE, "w") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"[WEATHER] Cache error: {e}")
    
    @staticmethod
    def _load_cached_weather(city: str) -> Optional[Dict]:
        """Load cached weather data if available"""
        try:
            if os.path.exists(WEATHER_CACHE):
                with open(WEATHER_CACHE, "r") as f:
                    cache = json.load(f)
                if city in cache:
                    return WeatherManager._format_weather(cache[city]["data"])
        except Exception as e:
            print(f"[WEATHER] Cache load error: {e}")
        return None


if __name__ == "__main__":
    # Test
    try:
        manager = WeatherManager()
        weather = manager.get_weather_by_city("London")
        print(json.dumps(weather, indent=2))
    except ValueError as e:
        print(f"Error: {e}")
