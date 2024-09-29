import PyPDF2
import pandas as pd
import json

# Ouvrir le fichier PDF
pdf_file = "/Users/mac/Downloads/EPHEMERIS .pdf"  # Remplacez par le chemin de votre fichier PDF
with open(pdf_file, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    number_of_pages = len(reader.pages)

    # Créer une structure de données pour stocker les informations
    ephemeris_data = {}

    # Lire chaque page du PDF et extraire les informations
    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text = page.extract_text()

        # Séparer chaque ligne pour analyser les données plus facilement
        lines = text.split("\n")
        for line in lines:
            # Chercher les lignes qui contiennent des informations sur les dates et les positions planétaires
            if "Jan" in line or "Feb" in line:  # Recherche des lignes avec des dates
                # Extraire la date et les positions planétaires
                parts = line.split()  # Diviser la ligne en parties
                date = " ".join(parts[:3])  # La date est dans les 3 premières parties
                planets_positions = parts[3:]  # Les positions des planètes sont les parties restantes
                
                # Créer une entrée dans le dictionnaire pour chaque date
                ephemeris_data[date] = {
                    "sun": float(planets_positions[0]),  # Exemple : position du Soleil
                    "moon": float(planets_positions[1]),  # Exemple : position de la Lune
                    "venus": float(planets_positions[2]),  # Position de Vénus
                    "mars": float(planets_positions[3])  # Position de Mars
                }

# Convertir les données en JSON
with open("ephemeris_data.json", "w") as json_file:
    json.dump(ephemeris_data, json_file, indent=4)

print("Les données des éphémérides ont été enregistrées dans 'ephemeris_data.json'.")
