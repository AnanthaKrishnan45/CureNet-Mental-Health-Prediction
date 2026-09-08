const chatLog = document.getElementById("chatLog");
const form = document.getElementById("chatForm");
const input = document.getElementById("userMessage");
const sendBtn = document.getElementById("sendBtn");
const typing = document.getElementById("typing");
const clearBtn = document.getElementById("clearBtn");

const sessionId = crypto.randomUUID ? crypto.randomUUID() : String(Date.now());

function addMessage(text, role = "bot", intent = "") {
  const row = document.createElement("div");
  row.className = `message ${role} ${intent}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function setLoading(loading) {
  typing.style.display = loading ? "block" : "none";
  sendBtn.disabled = loading;
}

async function sendMessage(messageOverride = null) {
  const message = (messageOverride ?? input.value).trim();
  if (!message) return;

  addMessage(message, "user");
  input.value = "";
  input.style.height = "auto";
  setLoading(true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message, session_id: sessionId})
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed");

    addMessage(data.response, "bot", data.intent === "crisis" ? "crisis" : "");
  } catch (error) {
    addMessage("I couldn't reach the backend. Please make sure the Flask server is running.", "bot");
    console.error(error);
  } finally {
    setLoading(false);
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage();
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 110) + "px";
});

document.querySelectorAll(".quick-actions button").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.message));
});

clearBtn.addEventListener("click", () => {
  chatLog.innerHTML = "";
  addMessage(
    "Hi, I'm CureNet. Tell me what you're experiencing. I can provide general mental-wellness information and coping ideas, but I can't diagnose a mental-health condition.",
    "bot"
  );
});

addMessage(
  "Hi, I'm CureNet. Tell me what you're experiencing. I can provide general mental-wellness information and coping ideas, but I can't diagnose a mental-health condition.",
  "bot"
);
