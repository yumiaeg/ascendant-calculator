import swisseph as swe

# Chemin vers les fichiers d'éphémérides
swe.set_ephe_path('/Users/mac/Desktop/swisseph_project/swisseph-master/ephe')  # Remplace par le chemin correct

# Exemple de calcul pour une date précise
year, month, day = 1993, 9, 27  # Par exemple, pour le 27 septembre 1993
julian_day = swe.julday(year, month, day)

# Calculer la position du soleil pour cette date
sun_position = swe.calc(julian_day, swe.SUN)[0]

# Afficher la position du soleil
print(f"Position du soleil : {sun_position} degrés")
