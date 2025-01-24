import json

def load_data(file_path="data/szabalyzat.json"):
    """Betölti a JSON formátumú könyvtárhasználati szabályzatot."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 🔹 Betöltjük az adatokat
data = load_data()

# 🔹 Keresünk egy pontos "Nyitvatartás" kulcsot
if "Nyitvatartás" in data:
    print("A 'Nyitvatartás' kulcs megtalálható a JSON fájlban!")
    print(f"Tartalom: {data['Nyitvatartás']}")
else:
    print("HIBA: A 'Nyitvatartás' kulcs NEM található a JSON fájlban!")
