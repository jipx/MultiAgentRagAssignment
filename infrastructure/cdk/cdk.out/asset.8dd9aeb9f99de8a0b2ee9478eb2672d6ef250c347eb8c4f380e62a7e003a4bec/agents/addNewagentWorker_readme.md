# 📦 How to Add a New Agent to the Worker Lambda in the Bedrock Multi-Agent RAG System

This guide explains how to integrate a new agent (e.g., `sc-labquiz-gen`) into the existing `worker_lambda` infrastructure of the Bedrock Multi-Agent system.

---

## 🧩 Architecture Overview

```
[Submit Lambda] --> [SQS] --> [Worker Lambda]
                                     ↓
                            [agent_router.py]
                                     ↓
                      [agents/{agent_name}_agent.py]
```

---

## 🚀 Steps to Add a New Agent

### 1. Create the Agent Handler File

Create a new file under:

```
backend/lambda_worker/agents/sc_labquiz_gen_agent.py
```

Example content:

```python
import os
import logging
from bedrock import call_bedrock_claude_json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_sc_labquiz_gen(question: str) -> str:
    system_prompt = """You are a lab assistant AI that generates secure coding lab quizzes from lab notes in markdown. Output only JSON in this format:
{
  "questions": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "C"
    }
  ]
}
"""
    return call_bedrock_claude_json(
        prompt=question,
        system_prompt=system_prompt,
        temperature=0.3,
        max_tokens=1024,
        stop_sequences=["\n\n"]
    )
```

---

### 2. Register the Agent in `agent_router.py`

Modify `backend/lambda_worker/agent_router.py`:

```python
from agents.sc_labquiz_gen_agent import handle_sc_labquiz_gen  # 🆕

def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    if topic == "owasp":
        return handle_owasp_question(question)
    elif topic == "assignment":
        return handle_assignment_question(question)
    elif topic == "cloudops":
        return handle_cloudops_question(question)
    elif topic == "sc-labquiz-gen":  # 🆕 Add this route
        return handle_sc_labquiz_gen(question)
    else:
        raise ValueError(f"❌ Invalid topic received: '{topic}'")
```

---

### 3. Use the Agent via `submit_lambda`

Ensure the `topic` or `agent` field in your SQS message is:

```json
{
  "topic": "sc-labquiz-gen",
  "agent": "sc-labquiz-gen",
  "question": "Your markdown lab notes here..."
}
```

This can be triggered via:

- Streamlit frontend
- Postman/API
- Direct invocation of the `ask` endpoint

---

### 4. (Optional) Retry on Failure

The `worker_lambda` will automatically raise exceptions to trigger SQS retry if the agent throws an error (e.g., throttling or timeout). Ensure your agent raises meaningful exceptions when appropriate.

---

### 5. Deploy the Changes

From your CDK directory:

```bash
cd infrastructure/cdk
cdk deploy
```

---

## ✅ Summary

| Step | Action |
|------|--------|
| 1 | Add `agents/my_agent.py` |
| 2 | Add route in `agent_router.py` |
| 3 | Ensure topic in SQS message matches |
| 4 | Deploy and test |

---

For more advanced use (few-shot examples, prompt chaining, fallback handling), reach out or extend your agent logic accordingly.
