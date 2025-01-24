import json
import re

def load_and_process_text(file_path):
    """Beolvassa és megtisztítja a könyvtárhasználati szabályzatot"""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Sorok összevonása és felesleges whitespace eltávolítása
    clean_text = re.sub(r"\s+", " ", text).strip()

    # Fejezetcímek azonosítása (pl. "1. Beiratkozás és használati szabályok")
    sections = re.split(r"\d+\.\s+", clean_text)
    section_titles = re.findall(r"\d+\.\s+(.+)", clean_text)

    # Strukturált JSON létrehozása
    structured_data = {title.strip(): sections[i + 1].strip() for i, title in enumerate(section_titles)}

    # JSON fájl mentése
    json_output = "data/szabalyzat.json"
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=4)

    print(f"📄 A szabályzat sikeresen feldolgozva és mentve: {json_output}")

if __name__ == "__main__":
    load_and_process_text("data/szabalyzat.txt")