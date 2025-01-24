import json
import re

def load_data(file_path="data/szabalyzat.json"):
    """Betölti a JSON formátumú szabályzatot."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def preprocess_query(query):
    """Eltávolítja az írásjeleket és kisbetűsíti a keresési kifejezést."""
    query = query.lower().strip()
    query = re.sub(r"[^\w\s]", "", query)  # Minden írásjelet eltávolít
    return query

def search_library_rules(query):
    """Egyszerű kereső, amely pontos egyezést keres."""
    data = load_data()
    query = preprocess_query(query)

    results = {title: content for title, content in data.items() if query in preprocess_query(title) or query in preprocess_query(content)}

    if results:
        print("Találatok:")
        for title, content in results.items():
            print(f"🔹 {title}: {content[:200]}...")
    else:
        print("HIBA: A kereső nem talált találatot!")

if __name__ == "__main__":
    search_library_rules("nyitvatartás")
