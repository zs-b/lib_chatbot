function askChatbot() {
    let userInput = document.getElementById("user-input").value.trim();
    if (userInput === "") return;

    addMessage(userInput, "user-message");
    document.getElementById("user-input").value = "";

    fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Szerverhiba: " + response.status);
        }
        return response.json();
    })
    .then(data => {
        addMessage(data.response, "bot-message");
    })
    .catch(error => {
        console.error("Hiba:", error);
        addMessage("Hiba történt a szerverrel való kapcsolódás során. Próbáld újra később!", "bot-message");
    });
}

// Üzenet hozzáadása a chatboxhoz
function addMessage(text, className) {
    let chatBox = document.getElementById("chat-box");
    let message = document.createElement("p");
    message.classList.add(className);
    message.innerText = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight; // Görgetés az aljára
}

// Enter billentyű lenyomására küldés
function handleKeyPress(event) {
    if (event.key === "Enter") {
        askChatbot();
    }
}