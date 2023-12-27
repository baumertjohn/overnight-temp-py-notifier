# A Python application fetching overnight temperatures from OpenWeather API and
# notifying users via email, SMS, or Pushbullet.

import os
import requests
from datetime import datetime, timedelta
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
    city_name = weather_data["city"]["name"]
    low_temps = []
    for i in range(40):
        time = weather_data["list"][i]["dt_txt"]
        if time[-8:] == "06:00:00":
            dt_object = datetime.utcfromtimestamp(weather_data["list"][i]["dt"])
            prev_day = (dt_object - timedelta(days=1)).strftime("%A")
            low_temp = int(weather_data["list"][i]["main"]["temp_min"])
            # day = dt_object.strftime("%A")
            # print(i, low_temp, time, day)
            low_temps.append({prev_day: low_temp})
    return city_name, low_temps


def create_message(city_name, low_temps):
    weather_message = f"{city_name} Overnight Forecast\n"
    for temp in low_temps:
        for key, value in temp.items():
            if value <= 39:
                warning = " ❄❄❄"
            else:
                warning = ""
            weather_message += f"{key} Night: {value}{warning}\n"
    return weather_message


def main():
    # lat, lon = find_lat_lon()
    city_name, low_temps = get_weather_data(ZIP_CODE, COUNTRY_CODE)
    weather_message = create_message(city_name, low_temps)
    print(weather_message)


if __name__ == "__main__":
    main()
