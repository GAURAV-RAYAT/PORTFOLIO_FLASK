const chatToggle = document.getElementById("chat-toggle");
const chatBox = document.getElementById("chat-box");
const chatClose = document.getElementById("chat-close");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatLog = document.getElementById("chat-log");

// Toggle Chat
chatToggle.addEventListener("click", () => {
  chatBox.classList.toggle("chat-hidden");
  if (!chatBox.classList.contains("chat-hidden")) {
      setTimeout(() => chatInput.focus(), 100); // Auto focus input
  }
});

// Close Chat
chatClose.addEventListener("click", () => {
  chatBox.classList.add("chat-hidden");
});

// Send Message
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  // 1. Add User Message
  appendMessage(message, "user-message");
  chatInput.value = "";

  // 2. Show Typing Indicator
  const typingDiv = document.createElement("div");
  typingDiv.className = "typing-indicator";
  typingDiv.textContent = "AI is typing...";
  chatLog.appendChild(typingDiv);
  scrollToBottom();

  try {
    // 3. Send to Backend
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    });
    const data = await res.json();

    // 4. Remove Typing & Add Bot Response
    chatLog.removeChild(typingDiv);
    appendMessage(data.response, "bot-message");

  } catch (err) {
    if(chatLog.contains(typingDiv)) chatLog.removeChild(typingDiv);
    appendMessage("Oops! Something went wrong. Try again.", "bot-message");
  }
});

function appendMessage(text, className) {
  const div = document.createElement("div");
  div.classList.add("chat-message", className);
  div.textContent = text;
  chatLog.appendChild(div);
  scrollToBottom();
}

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}