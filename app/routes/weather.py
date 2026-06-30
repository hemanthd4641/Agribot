"""Weather route blueprint.

Provides REST endpoints for fetching current weather and forecasts
via the WeatherService.
"""

from flask import Blueprint, current_app, jsonify, request

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/weather', methods=['GET'])
def get_weather():
    """Get complete weather info (current + forecast) for a city.
    
    Query Params:
        city (str): City name to search for.
    """
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
        
    weather_service = current_app.weather_service
    result = weather_service.get_weather_for_city(city)
    
    if result.get('status') == 'error':
        return jsonify({'error': result.get('message')}), 404
        
    return jsonify(result)


@weather_bp.route('/weather/current', methods=['GET'])
def get_current_weather():
    """Get only the current weather for a city."""
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
        
    weather_service = current_app.weather_service
    result = weather_service.get_weather_for_city(city)
    
    if result.get('status') == 'error':
        return jsonify({'error': result.get('message')}), 404
        
    return jsonify({
        'status': 'success',
        'location': result['location'],
        'current': result['weather'].get('current')
    })


@weather_bp.route('/weather/forecast', methods=['GET'])
def get_weather_forecast():
    """Get only the 7-day forecast for a city."""
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400
        
    weather_service = current_app.weather_service
    result = weather_service.get_weather_for_city(city)
    
    if result.get('status') == 'error':
        return jsonify({'error': result.get('message')}), 404
        
    return jsonify({
        'status': 'success',
        'location': result['location'],
        'daily': result['weather'].get('daily')
    })
