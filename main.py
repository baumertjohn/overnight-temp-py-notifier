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


def get_weather_data(zip_code, country_code):
    """
    Retrieves weather forecast data for a given ZIP code and country code from the OpenWeatherMap API.

    Args:
        zip_code (str): The ZIP code of the location.
        country_code (str): The country code of the location.

    Returns:
        Tuple[str, List[Dict[str, Union[str, int]]]]: A tuple containing the city name and a list of dictionaries,
        each representing the lowest temperatures for the corresponding day and night.

    Example:
        >>> city, low_temps = get_weather_data("12345", "US")
    """
    params = {
        "zip": f"{zip_code},{country_code}",
        "appid": OPENWEATHER_API_KEY,
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
            low_temps.append({prev_day: low_temp})
    return city_name, low_temps


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
    for temp in low_temps:
        for key, value in temp.items():
            if value <= 39:
                warning = " ❄❄❄"
            else:
                warning = ""
            weather_message += f"{key} night: {value}{warning}\n"
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
    # Get city name and 5 day low temps from openweathermap
    print("Getting weather data")
    city_name, low_temps = get_weather_data(ZIP_CODE, COUNTRY_CODE)

    # Create weather message from day / temp dict
    print("Creating message")
    weather_message = create_message(low_temps)

    # Send formatted message to user
    print("Sending weather email")
    send_email_message(city_name, weather_message)


if __name__ == "__main__":
    main()
