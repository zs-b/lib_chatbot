from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from src.chatbot import chatbot_response

app = Flask(__name__)
CORS(app)  # Engedélyezi a másik domainről érkező kéréseket

@app.route("/")
def home():
    """Betölti az index.html oldalt"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """API végpont a chatbot számára"""
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"error": "Üres kérdés"}), 400

    response = chatbot_response(user_input)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)