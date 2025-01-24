import json
import re
from fuzzywuzzy import process

def load_data(file_path="data/szabalyzat.json"):
    """Betölti a JSON formátumú könyvtárhasználati szabályzatot."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def preprocess_text(text):
    """Egyszerűsített szövegfeldolgozás kereséshez (kisbetűsítés, írásjelek eltávolítása)."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Írásjelek eltávolítása
    return text

def search_library_rules(query, top_n=3):
    """Kulcsszavas keresés a szabályzatban (rugalmas keresőmotor)."""
    data = load_data()
    titles = list(data.keys())

    # Fuzzy keresés a szabályzat címei között
    best_matches = process.extract(query, titles, limit=top_n)

    # Csak azokat vesszük figyelembe, ahol a találat pontszám > 50
    return {title: data[title] for title, score in best_matches if score > 50} or \
        {"Nincs találat": "A keresett információ nem található a szabályzatban."}

if __name__ == "__main__":
    print("Könyvtári chatbot - Írja be a kérdést vagy kilépéshez, hogy 'vége'.")

    while True:
        query = input("\nMit szeretne tudni a könyvtárról? ")
        if query.lower() in ["vége", "exit", "kilépés"]:
            print("Köszönöm a kérdéseket! Viszlát!")
            break

        results = search_library_rules(query)
        for title, content in results.items():
            print(f"\n {title}\n{content[:300]}...")  # Csak az első 300 karaktert mutatja