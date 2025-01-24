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

# Fuzzy keresés a szabályzatban
def search_library_rules(query, top_n=3):
    """Kulcsszavas és fuzzy keresés a szabályzatban."""
    query = query.lower()
    titles = list(data.keys())

    # Fuzzy keresés a címek között
    best_matches = process.extract(query, titles, limit=top_n)
    results = {title: data[title] for title, score in best_matches if score > 50}

    if not results:
        return "A kérdésre nem található információ a szabályzatban."
    
    return next(iter(results.values()))  # Az első találatot visszaadjuk

# Google Gemini API hívás
def ask_gemini(query):
    """A Gemini API használata a válasz generálásához."""
    context = search_library_rules(query)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"A könyvtár szabályzata alapján válaszolj: {context}")
    return response.text if response else "Hiba történt a válasz generálásakor."

# Gradio UI
def chatbot_interface(user_input):
    """A chatbot fő interfésze."""
    response = ask_gemini(user_input)
    return response

# Gradio alkalmazás
iface = gr.Interface(
    fn=chatbot_interface,
    inputs=gr.Textbox(lines=2, placeholder="Írja be a kérdést...", label="Kérdés: "),
    outputs=gr.Textbox(label="Válasz: "),
    title="Könyvtári Chatbot",    
    description="Ez a chatbot válaszokat ad a könyvtárhasználati szabályzat alapján.",
    live=True,
    clear_btn="Törlés",
    theme="compact",
    allow_flagging="never",
    css="static/style.css"
)

# Indítás
if __name__ == "__main__":
    iface.launch()