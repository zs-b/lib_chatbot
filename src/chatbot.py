import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import difflib
import re

# API kulcs betöltése
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Hiba: nincs API kulcs beállítva az .env fájlban!")
genai.configure(api_key=API_KEY)

# A szabályzat JSON formátumú adatbetöltése
def load_data(file_path="data/szabalyzat.json"):
    """Betölti a JSON formátumú könyvtárhasználati szabályzatot."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Szöveg előfeldolgozása a kereséshez
def preprocess_query(query):
    """Eltávolítja az írásjeleket és kisbetűsíti a keresési kifejezést."""
    query = query.lower().strip()
    query = re.sub(r"[^\w\s]", "", query)  # Minden írásjel eltávolítása
    return query

# Kereső funkció (rugalmas keresés)
def search_library_rules(query, top_n=3):
    """Kulcsszavas és hasonlósági keresés a szabályzatban."""
    data = load_data()
    query = preprocess_query(query)

    # Egyszerű keresés (pontosan tartalmazza-e a kérdést?)
    results = {title: content for title, content in data.items() if query in preprocess_query(title) or query in preprocess_query(content)}

    # Hasonlósági keresés, ha nincs pontos egyezés
    if not results:
        best_match = difflib.get_close_matches(query, [preprocess_query(t) for t in data.keys()], n=1, cutoff=0.5)
        if best_match:
            original_title = [title for title in data.keys() if preprocess_query(title) == best_match[0]][0]
            results[original_title] = data[original_title]

    return dict(list(results.items())[:top_n]) if results else {"Nincs találat": "A keresett információ nem található a szabályzatban."}

# Gemini API hívás
def ask_gemini(context, query):
    """A keresett szabályzat alapján válasz generálása a Gemini LLM-mel."""
    model = genai.GenerativeModel("gemini-1.5-flash")
     # Levágjuk a szöveget, hogy ne legyen túl hosszú
    trimmed_context = context[:400]  # Maximum 400 karakteres prompt, mert mindig timeout-ol
    prompt = (
        f"A könyvtár szabályzatából keresett releváns információ:\n\n"
        f"{trimmed_context}\n\n"
        f"A fenti információk alapján válaszolj röviden és tömören:\n\n"
        f"Kérdés: {query}"
    )
    try:
        response = model.generate_content(prompt)
        return response.text if response else "Hiba történt a válasz generálásakor."
    except Exception as e:
        return f"Hiba történt a Gemini API hívás során: {str(e)}"

# Chatbot fő funkció
def chatbot_response(query):
    """A felhasználói kérdés feldolgozása: keresés a szabályzatban és válaszgenerálás."""
    search_results = search_library_rules(query)
    
    if "Nincs találat" in search_results:
        return "A kérdésre nem található információ a szabályzatban."

    # 🔹 Ha több találat van, csak az elsőt használjuk, hogy ne legyen túl hosszú
    first_result_title, first_result_content = next(iter(search_results.items()))

    print(f"Keresési találat a Gemini számára: {first_result_title}: {first_result_content[:200]}...")  # DEBUG

    return ask_gemini(first_result_content, query)

# Teszt futtatás
if __name__ == "__main__":
    user_question = input("Kérdés: ")
    response = chatbot_response(user_question)
    print("\n💬 Chatbot válasza:\n", response)