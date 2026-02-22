# 🤖 Gaurav Rayat AI Agent API

This API allows you to interact with an AI agent trained on **Gaurav Rayat's** professional background, including his Resume and LinkedIn profile.

The system uses **LangChain** and **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers.

---

## 🚀 Endpoint

* **URL:** `https://gauravrayat.me/api/ask`
* **Method:** `POST`
* **Content-Type:** `application/json`

---

## 🛠 Usage Examples

### 1️⃣ Python (Recommended)

The most flexible way to interact with the API. This script allows for a continuous chat session.

```python
import requests

def ask_ai():
    url = "https://gauravrayat.me/api/ask"
    headers = {"Content-Type": "application/json"}

    print("AI Agent: Ask me anything about Gaurav's experience!")

    while True:
        question = input("You: ")
        if question.lower() in ['exit', 'quit']:
            break

        response = requests.post(
            url,
            json={"question": question},
            headers=headers
        )

        if response.status_code == 200:
            print(f"AI: {response.json().get('answer')}\n")
        else:
            print("Error: Could not reach the agent.")

if __name__ == "__main__":
    ask_ai()
```

---

### 2️⃣ PowerShell

Perfect for a quick query from the Windows terminal.

```powershell
$body = @{ question = "What is Gaurav's AIR in GATE 2025?" } | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "https://gauravrayat.me/api/ask" `
  -ContentType "application/json" `
  -Body $body
```

---

### 3️⃣ cURL (Terminal / Bash)

For Linux, macOS, or standard CMD users.

```bash
curl -X POST https://gauravrayat.me/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What technologies does Gaurav know?"}'
```

---

## 📝 Request Format

The API expects a JSON object with a single key:

| Key      | Type   | Description                                     |
| -------- | ------ | ----------------------------------------------- |
| question | string | The specific question you want to ask the agent |

### Example Request

```json
{
  "question": "What is Gaurav's background in Data Science?"
}
```

---

## 📦 Response Format

The API returns a JSON object:

```json
{
  "answer": "Gaurav Rayat is a Mathematics (Hons.) student at Delhi University with a strong interest in Data Science and Agentic AI..."
}
```

---

## 🔒 Security & Privacy

* This API is public and intended for professional inquiries.
* Rate limiting is applied to prevent abuse via the Vercel Firewall.
* No personal user data is stored.
* Queries are processed in real-time against professional documents only.

---

## 📌 Tech Stack

* LangChain
* Retrieval-Augmented Generation (RAG)
* OpenAI
* Vercel (Deployment & Firewall)

---

© 2026 Gaurav Rayat | Data Science & AI Enthusiast