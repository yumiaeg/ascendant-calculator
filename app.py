from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime, timedelta
import requests  # Used to query the Google Timezone API
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https:www.welcometoyumiverse.com"}})

# Function to adjust local time to GMT based on the location (latitude/longitude)
def adjust_to_gmt(date_str, time_str, latitude, longitude, google_api_key):
    """
    Adjusts the given date and time based on the timezone fetched from Google Timezone API.
    Returns the date and time in GMT.
    """
    # Convert the date and time into a timestamp
    birth_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    timestamp = int(birth_datetime.timestamp())  # Convert to Unix timestamp

    # Google Timezone API request
    timezone_api_url = f"https://maps.googleapis.com/maps/api/timezone/json?location={latitude},{longitude}&timestamp={timestamp}&key={google_api_key}"
    response = requests.get(timezone_api_url)
    timezone_data = response.json()

    if timezone_data['status'] != 'OK':
        raise Exception(f"Error fetching timezone data: {timezone_data['status']}")

    # Extract timezone offset and DST offset
    dst_offset = timezone_data['dstOffset']  # Daylight saving time offset in seconds
    raw_offset = timezone_data['rawOffset']  # Timezone offset from UTC in seconds

    # Calculate total offset from UTC
    total_offset_seconds = dst_offset + raw_offset

    # Adjust the birth datetime based on the total offset
    gmt_datetime = birth_datetime - timedelta(seconds=total_offset_seconds)

    # Log the result
    print(f"Local time: {birth_datetime}, GMT time: {gmt_datetime}")

    return gmt_datetime

@app.route('/calculate_ascendant', methods=['POST'])
def calculate_ascendant():
    try:
        # Affiche les données reçues
        data = request.get_json()
        print(f"Data received: {data}")
        
        birth_date = data['date']
        birth_time = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        google_api_key = os.getenv('GOOGLE_API_KEY')  # Utilisation de la variable d'environnement
        timezone_api_key = os.getenv('TIMEZONE_API_KEY')
        # Adjust local time to GMT using Google Timezone API
        gmt_datetime = adjust_to_gmt(birth_date, birth_time, latitude, longitude, google_api_key)

        # Extract the adjusted date and time
        adjusted_date = gmt_datetime.strftime("%Y-%m-%d")
        adjusted_time = gmt_datetime.strftime("%H:%M")

        # Calculate the ascendant based on the adjusted GMT date and time
        ascendant = calculate_ascendant_logic(adjusted_date, adjusted_time, latitude, longitude)
        
        return jsonify({'ascendant': ascendant}), 200

    except Exception as e:
        print(f"Error: {e}")  # Affiche l'erreur dans le terminal
        return jsonify({'error': str(e)}), 400


def calculate_ascendant_logic(birth_date, birth_time, latitude, longitude):
    """
    Precise calculation of the ascendant using Swiss Ephemeris.
    """
    # Convert the date and time into a datetime object
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    
    # Extract the year, month, day, and decimal hour
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day
    hour = birth_datetime.hour + birth_datetime.minute / 60  # Decimal format for the hour

    # Initialize Swiss Ephemeris and calculate the Julian Day
    swe.set_ephe_path('/usr/share/ephe')  # Adjust the path as needed
    julian_day = swe.julday(year, month, day, hour)

    # Calculate the Greenwich Sidereal Time (GST)
    gst = swe.sidtime(julian_day)

    # Adjust for the local sidereal time (LST), accounting for longitude
    lst = gst + (longitude / 15.0)  # Convert longitude to hours

    # Calculate the astrological houses and retrieve the ascendant
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b'P')  # Using 'P' for Placidus

    ascendant_degree = ascmc[0]  # The ascendant is the first item in the list of ascmc

    # Log the ascendant degree
    print(f"Ascendant degree: {ascendant_degree}")

    # Convert the degrees into an astrological sign
    ascendant_sign = convert_degree_to_sign(ascendant_degree)

    return ascendant_sign


def convert_degree_to_sign(degree):
    """
    Convert degrees to an astrological sign.
    """
    signs = ["Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge", 
             "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons"]
    sign_index = int(degree // 30)  # Each sign spans 30 degrees
    return signs[sign_index]


if __name__ == '__main__':
    app.run(debug=True)
