# A Python application fetching overnight temperatures from OpenWeather API and
# notifying users via email, SMS, or Pushbullet.

import os
import requests
import smtplib
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
SEND_FROM_EMAIL = os.environ.get("SEND_FROM_EMAIL")
SEND_FROM_PASSWORD = os.environ.get("SEND_FROM_PASSWORD")
SMTP_ADDRESS = os.environ.get("SMTP_ADDRESS")
SEND_TO_EMAIL = os.environ.get("SEND_TO_EMAIL")

# Location to do weather search
ZIP_CODE = "80615"
COUNTRY_CODE = "us"


def find_lat_lon(zip_code, country_code):
    """
    Fetches city name, latitude, and longitude data for a given ZIP code and country code using the OpenWeatherMap API.

    Args:
        zip_code (str): The ZIP code of the location.
        country_code (str): The country code of the location.

    Returns:
        Tuple[str, float, float]: A tuple containing the city name, latitude, and longitude information.

    Example:
        >>> city, latitude, longitude = find_lat_lon("12345", "US")
    """
    params = {
        "zip": f"{zip_code},{country_code}",
        "appid": OPENWEATHER_API_KEY,
    }
    response = requests.get("http://api.openweathermap.org/geo/1.0/zip", params=params)
    lat_lon_data = response.json()
    return lat_lon_data["name"], lat_lon_data["lat"], lat_lon_data["lon"]


def get_weather_data(lat, lon):
    """
    Retrieves 8-day weather forecast data for a given latitude and longitude from the OpenWeatherMap API.

    Args:
        lat (float): The latitude of the location.
        lon (float): The longitude of the location.

    Returns:
        List[Dict[str, Union[str, int]]]: A list of dictionaries, each representing the lowest temperatures
        for the corresponding day and night over the next 8 days.

    Example:
        >>> low_temps = get_weather_data(40.7128, -74.0060)
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "exclude": "current,minutely,hourly",
        "units": "imperial",
    }
    response = requests.get(
        "https://api.openweathermap.org/data/3.0/onecall", params=params
    )
    weather_data = response.json()
    num_of_days = len(weather_data["daily"])
    low_temps = []
    for i in range(num_of_days):
        dt_object = datetime.utcfromtimestamp(weather_data["daily"][i]["dt"])
        day = dt_object.strftime("%A")
        low_temp = int(weather_data["daily"][i]["temp"]["min"])
        low_temps.append({day: low_temp})
    return low_temps


def create_message(low_temps):
    """
    Creates a weather message based on the provided low temperature data.

    Args:
        low_temps (List[Dict[str, int]]): A list of dictionaries, each representing the lowest temperature
        for a specific day and night.

    Returns:
        str: A formatted weather message indicating the low temperatures for each day and night.

    Example:
        >>> low_temps = [{'Monday': 35}, {'Tuesday': 32}, {'Wednesday': 28}]
        >>> message = create_message(low_temps)
    """
    weather_message = ""
    overnight = True
    for temp in low_temps:
        for key, value in temp.items():
            if value <= 39:
                warning = " ❄❄❄"
            else:
                warning = ""
            # Set "Overnight" for first day of list
            if not overnight:
                day = f"{key} night"
            else:
                day = "Overnight"
                overnight = False
            weather_message += f"{day}: {value}{warning}\n"
    return weather_message


def send_email_message(city_name, weather_message):
    """
    Sends an email with the overnight weather forecast message.

    Args:
        city_name (str): The name of the city for which the weather forecast is generated.
        weather_message (str): The weather message containing low temperature information.

    Returns:
        None

    Example:
        >>> city_name = "Eaton"
        >>> weather_message = "Monday night: 35 ❄❄❄\nTuesday night: 32 ❄❄❄\n"
        >>> send_email_message(city_name, weather_message)
    """
    email_message = f"Subject: {city_name} Overnight Forecast\n\n{weather_message}"
    with smtplib.SMTP(SMTP_ADDRESS, 587) as connection:
        connection.starttls()
        connection.login(user=SEND_FROM_EMAIL, password=SEND_FROM_PASSWORD)
        connection.sendmail(
            from_addr=SEND_FROM_EMAIL,
            to_addrs=SEND_TO_EMAIL,
            msg=email_message.encode("utf-8"),
        )


def main():
    """
    Fetches weather data, creates a weather message, and sends an email with the overnight forecast.

    This function serves as the entry point for the weather app, orchestrating the entire process
    of retrieving weather data, generating a message, and sending an email to the user.

    Args:
        None

    Returns:
        None

    Example:
        >>> main()
    """
    # Get city name and latitude and longitude based on ZIP from Openweathermap Geocoding API
    city_name, lat, lon = find_lat_lon(ZIP_CODE, COUNTRY_CODE)

    # Get 8 day low temps from Openweathermap One Call API 3.0
    low_temps = get_weather_data(lat, lon)

    # Create weather message from day / temp dict
    weather_message = create_message(low_temps)

    # Send formatted message to user
    send_email_message(city_name, weather_message)


if __name__ == "__main__":
    main()
