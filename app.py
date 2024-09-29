from flask import Flask, request, jsonify
import swisseph as swe
from datetime import datetime
from pytz import timezone
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Fonction pour ajuster l'heure locale en heure GMT en tenant compte de l'heure d'été/hiver
def adjust_to_gmt(date_str, time_str, tz_name='Europe/Paris'):
    """
    Ajuste la date et l'heure données en fonction du fuseau horaire et de l'heure d'été/hiver.
    Retourne la date et l'heure en GMT.
    """
    local_tz = timezone(tz_name)
    naive_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    local_datetime = local_tz.localize(naive_datetime, is_dst=None)  # Ajoute le fuseau horaire local
    utc_datetime = local_datetime.astimezone(timezone('UTC'))  # Convertit en UTC (GMT)
    
    # Log pour vérifier l'ajustement de l'heure
    print(f"Heure locale : {local_datetime}, Heure GMT : {utc_datetime}")
    
    return utc_datetime

@app.route('/calculate_ascendant', methods=['POST'])
def calculate_ascendant():
    try:
        data = request.get_json()
        birth_date = data['date']
        birth_time = data['time']
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # Ajuster l'heure locale en GMT
        gmt_datetime = adjust_to_gmt(birth_date, birth_time, tz_name='Europe/Paris')

        # Extraire l'heure ajustée
        adjusted_date = gmt_datetime.strftime("%Y-%m-%d")
        adjusted_time = gmt_datetime.strftime("%H:%M")

        # Appel à la fonction pour calculer l'ascendant avec l'heure ajustée
        ascendant = calculate_ascendant_logic(adjusted_date, adjusted_time, latitude, longitude)
        
        return jsonify({'ascendant': ascendant}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400


def calculate_ascendant_logic(birth_date, birth_time, latitude, longitude):
    """
    Calcul précis de l'ascendant en utilisant Swiss Ephemeris
    """
    # Convertir la date et l'heure en format datetime
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    
    # Extraire les composants de la date et de l'heure
    year = birth_datetime.year
    month = birth_datetime.month
    day = birth_datetime.day
    hour = birth_datetime.hour + birth_datetime.minute / 60  # Heure au format décimal

    # Initialiser Swiss Ephemeris et calculer le jour Julien
    swe.set_ephe_path('/usr/share/ephe')  # Ajuster le chemin si nécessaire
    julian_day = swe.julday(year, month, day, hour)

    # Calcul du temps sidéral de Greenwich (GST)
    gst = swe.sidtime(julian_day)

    # Ajuster pour le temps sidéral local (LST) en tenant compte de la longitude
    lst = gst + (longitude / 15.0)  # Conversion de la longitude en heures

    # Calculer les maisons astrologiques et obtenir l'ascendant
    cusps, ascmc = swe.houses(julian_day, latitude, longitude, b'P')  # Utiliser 'P' pour Placidus

    ascendant_degree = ascmc[0]  # L'ascendant est le premier élément de la liste ascmc

    # Log du degré de l'ascendant
    print(f"Degré de l'ascendant : {ascendant_degree}")

    # Conversion des degrés en signe astrologique
    ascendant_sign = convert_degree_to_sign(ascendant_degree)

    return ascendant_sign


def convert_degree_to_sign(degree):
    """
    Convertir des degrés en un signe astrologique
    """
    signs = ["Bélier", "Taureau", "Gémeaux", "Cancer", "Lion", "Vierge", 
             "Balance", "Scorpion", "Sagittaire", "Capricorne", "Verseau", "Poissons"]
    sign_index = int(degree // 30)  # Chaque signe couvre 30 degrés
    return signs[sign_index]


if __name__ == '__main__':
    app.run(debug=True)