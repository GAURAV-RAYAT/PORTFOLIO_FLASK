document.getElementById("chat-toggle").addEventListener("click", function () {
  const chatBox = document.getElementById("chat-box");
  chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none";
});

document.getElementById("chat-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const chatLog = document.getElementById("chat-log");

  const userMessage = input.value.trim();
  if (!userMessage) return;

  chatLog.innerHTML += `<div><strong>You:</strong> ${userMessage}</div>`;
  input.value = "";

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMessage })
    });
    const data = await res.json();
    chatLog.innerHTML += `<div><strong>Bot:</strong> ${data.response}</div>`;
    chatLog.scrollTop = chatLog.scrollHeight;
  } catch (err) {
    chatLog.innerHTML += `<div><strong>Bot:</strong> Something went wrong!</div>`;
  }
});
