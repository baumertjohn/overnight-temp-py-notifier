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


def get_weather_data(zip_code, country_code):
    """
    TODO: create doc string for this function
    """
    # Example
    # api.openweathermap.org/data/2.5/forecast?zip={zip code},{country code}&appid={API key}
    params = {
        "zip": f"{zip_code},{country_code}",
        "appid": openweather_api_key,
        "units": "imperial",
    }
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast", params=params
    )
    weather_data = response.json()
    for i in range(40):
        time = weather_data['list'][i]["dt_txt"]
        if time[-8:] == "06:00:00":
            low_temp = int(weather_data['list'][i]['main']["temp_min"])
            print(i, low_temp, time)
    


def main():
    # lat, lon = find_lat_lon()
    # print(f"Requested latitude and longitude is: {lat}, {lon}")

    get_weather_data(ZIP_CODE, COUNTRY_CODE)


if __name__ == "__main__":
    main()
