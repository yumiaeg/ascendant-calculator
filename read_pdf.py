import PyPDF2

# Ouvrir le fichier PDF
pdf_file = "/Users/mac/Downloads/EPHEMERIS 2000-2050.pdf"
with open(pdf_file, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    number_of_pages = len(reader.pages)
    
    # Lire le contenu de chaque page
    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text = page.extract_text()
        print(f"Page {page_number + 1}:")
        print(text)
import PyPDF2
import pandas as pd  # Ajoutez cette ligne

# Mettre à jour le chemin vers votre nouveau fichier PDF
pdf_file = "/Users/mac/Downloads/EPHEMERIS .pdf"  # Mettez ici le chemin correct vers le nouveau fichier
with open(pdf_file, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    number_of_pages = len(reader.pages)

    data = []  # Liste pour stocker les données

    # Lire le contenu de chaque page
    for page_number in range(number_of_pages):
        page = reader.pages[page_number]
        text = page.extract_text()

        # Sépare chaque ligne pour analyser les données plus facilement
        lines = text.split("\n")
        for line in lines:
            if "Jan" in line or "Feb" in line:  # Rechercher les lignes avec des dates
                data.append(line)

# Convertir la liste en un tableau pandas
df = pd.DataFrame(data, columns=["Date et positions"])
print(df)


