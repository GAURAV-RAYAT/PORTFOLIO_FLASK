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

## 🤝 Multi-Agent Website Operations (Roadmap)

If you want `gauravrayat.me` to be managed by multiple AI agents (monitoring, analytics, security, and recovery), the safest path is to start with a **human-supervised multi-agent architecture** and then gradually increase autonomy.

### Suggested Agent Roles

1. **Monitoring Agent**
   * Watches uptime, 4xx/5xx spikes, latency, and broken routes.
   * Triggers alerts when thresholds are crossed.
2. **Data Agent**
   * Collects approved analytics events and summarizes trends.
   * Publishes daily/weekly reports for the coordinator.
3. **Security Agent**
   * Detects bot spikes, suspicious IP patterns, and abuse attempts.
   * Recommends or executes safe, pre-approved mitigations.
4. **Action/Fix Agent**
   * Handles bounded remediations such as restarts, cache purge, or rollback.
   * Must be restricted by allowlists and audit logs.
5. **Coordinator Agent**
   * Receives events from all agents and chooses workflows.
   * Escalates high-risk changes for human approval.

### Agent Communication Layer

Use an event bus so agents can collaborate without tight coupling:

* Redis Pub/Sub (simple start)
* RabbitMQ / Kafka (higher scale and replayability)

Example flow:

`Monitoring Agent -> "500_error_spike" -> Coordinator -> Action Agent -> "restart+verify" -> Monitoring Agent confirms recovery`

### Safety Controls (Required)

* Human approval gate for destructive actions.
* Immutable audit trail for every agent decision/action.
* Per-agent permission scopes (least privilege).
* Circuit breaker to disable autonomous actions globally.

### Incremental Rollout Plan

* **Phase 1:** Monitoring + alerts only.
* **Phase 2:** Add analytics/data agent and coordinator summaries.
* **Phase 3:** Add limited auto-remediation for low-risk incidents.
* **Phase 4:** Add security automation and cross-agent playbooks.

This roadmap gives you the "AI-native autonomous portfolio" goal while keeping reliability and security under control.

---

## 🛰️ Implemented Now: Phase 1 (Monitoring + Alerts)

The project now includes a Phase-1 monitoring agent implementation:

* `GET /api/health` for uptime/health probing.
* `POST /api/monitoring/run` to execute one monitoring cycle.
* `scripts/run_monitoring_agent.py` for cron/scheduler execution.
* Email alerts on sustained failures and recovery notifications.

### Environment Variables

Configure these for monitoring:

* `MONITOR_TARGETS` (comma-separated URLs)
* `MONITOR_TIMEOUT_SECONDS` (default: `10`)
* `MONITOR_FAILURE_THRESHOLD` (default: `3`)
* `MONITOR_ALERT_EMAIL` (default: `gaurav.rayat2004@gmail.com`)
* `MONITOR_RUN_TOKEN` (optional; required as `X-Monitor-Token` header for `POST /api/monitoring/run` when set)

### Quick Start

```bash
python scripts/run_monitoring_agent.py
```

You can run this every 1-5 minutes using cron, GitHub Actions schedule, or any external scheduler.

### GitHub Actions (Already Added)

A workflow is included at:

* `.github/workflows/monitoring_agent.yml`

It runs every **2 hours** and calls your monitoring endpoint. Configure these repository secrets:

* `MONITORING_URL` (example: `https://gauravrayat.me/api/monitoring/run`)
* `MONITOR_RUN_TOKEN` (optional but recommended, if `MONITOR_RUN_TOKEN` is set on server)

---

© 2026 Gaurav Rayat | Data Science & AI Enthusiast
