# A Python application fetching overnight temperatures from OpenWeather API and
# notifying users via email, SMS, or Pushbullet.

import os
import requests
from dotenv import load_dotenv

load_dotenv()

openweather_api_key = os.environ.get("OPENWEATHER_API_KEY")

# TEMPS FOR TESTING
ZIP_CODE = "80615"
COUNTRY_CODE = "us"


def find_lat_lon():
    """
    Fetches latitude and longitude data for a given ZIP code and country code using the OpenWeatherMap API.

    Returns:
    Tuple[float, float]: A tuple containing latitude and longitude information.
    """
    params = {
        "zip": f"{ZIP_CODE},{COUNTRY_CODE}",
        "appid": openweather_api_key,
    }
    response = requests.get("http://api.openweathermap.org/geo/1.0/zip", params=params)
    lat_lon_data = response.json()
    return lat_lon_data["lat"], lat_lon_data["lon"]


def get_weather_data(lat, lon):
    """
    TODO: create doc string for this function
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": openweather_api_key,
    }
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast", params=params
    )
    weather_data = response.json()
    print(weather_data)


def main():
    lat, lon = find_lat_lon()
    print(f"Requested latitude and longitude is: {lat}, {lon}")

    get_weather_data(lat, lon)


if __name__ == "__main__":
    main()
