import gradio as gr
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from fuzzywuzzy import process

# API kulcs betöltése
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Hiba: nincs API kulcs beállítva!")

genai.configure(api_key=API_KEY)

# Szabályzat JSON betöltése
def load_data(file_path="szabalyzat.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

# Szinonima térképezés
synonyms = {
    "nyitva tartás": "nyitvatartás",
    "mikor van nyitva": "nyitvatartás",
    "tagsági díj": "tagság",
    "kölcsönzési idő": "kölcsönzés",
    "cím": "elérhetőségek"
}

def search_library_rules(query, top_n=3):
    """Kulcsszavas és fuzzy keresés a szabályzatban."""
    query = query.lower().strip()

    # Szinonima ellenőrzés 
    for key, value in synonyms.items():
        if key in query:
            query = query.replace(key, value)

    # Ha a kérdés könyv keresésére vonatkozik, irányítsuk az OPAC katalógushoz
    if any(word in query for word in ["keresem", "könyv", "dokumentum"]):
        opac_base_url = "https://opac3.kjk.qulto.eu/"
        return f"A könyvtári szabályzat nem tartalmaz információt konkrét dokumentumokról. A keresett könyvet itt találhatja meg: [OPAC katalógus]({opac_base_url})"

    titles = list(data.keys())

    # Dinamikus küszöbérték
    threshold = 80 if len(query) > 5 else 60

    # Fuzzy keresés a címek között
    best_matches = process.extract(query, titles, limit=top_n)
    results = {title: data[title] for title, score in best_matches if score > threshold}

    # Többszintű keresés, ha nincs találat
    if not results and threshold > 50:
        best_matches = process.extract(query, titles, limit=top_n)
        results = {title: data[title] for title, score in best_matches if score >= 40}

    # OPAC integráció konkrét dokumentum kereséséhez
    if not results:
        return "A kérdésre nem található információ a szabályzatban."

    return next(iter(results.values()))  # Az első találatot visszaadjuk

# Google Gemini API hívás
def ask_gemini(query):
    """A Gemini API használata a válasz generálásához, könyvkeresés figyelembe vételével."""
    try:
        context = search_library_rules(query)

        # Ha az OPAC katalógus linkjét adta vissza a kereső, akkor azt adjuk vissza
        if "opac3.kjk.qulto.eu" in context:
            return context

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"A könyvtár szabályzata alapján válaszolj: {context}")
        return response.text if response else "Hiba történt a válasz generálásakor."
    except Exception as e:
        return f"Hiba történt: {str(e)}. Próbálja újra később."

# Gradio UI
def chatbot_interface(user_input):
    """A chatbot fő interfésze."""
    response = ask_gemini(user_input)
    return response

css = """
.gradio-container { 
    background-color: #BFBBA9;
    font-family: 'Arial', sans-serif; 
}

.block { 
    background-color: #EAE2C6;
    border-radius: 10px; 
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.gr-textbox { 
    font-size: 16px; 
    border: 2px solid #98D8EF; 
    border-radius: 5px;
}

button { 
    background-color: #98D8EF !important; 
    color: white !important; 
    font-size: 16px;
    font-weight: bold;
    padding: 10px 15px;
    border-radius: 5px;
    cursor: pointer;
}

button:hover { 
    background-color: #BFBBA9 !important;
}

.gr-clear { 
    background-color: #98D8EF !important; 
    color: white !important; 
    font-size: 14px;
    font-weight: bold;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
}

.gr-clear:hover { 
    background-color: #BFBBA9 !important;
}

h1, h2 { 
    color:rgb(48, 122, 149); 
    font-size: 22px; 
}
"""

# Gradio alkalmazás
iface = gr.Interface(
    fn=chatbot_interface,
    inputs=gr.Textbox(lines=2, placeholder="Írja be a kérdést...", label="Kérdés: "),
    outputs=gr.Markdown(label="Válasz: "),
    title="Könyvtári Chatbot",    
    description="Ez a chatbot válaszokat ad a könyvtárhasználati szabályzat alapján.",
    live=True,
    clear_btn="Törlés",
    theme="compact",
    allow_flagging="never",
    css=css
)

# Indítás
if __name__ == "__main__":
    iface.launch()