
# 🛡️ OWASP Agent – Secure Coding Assistant using Amazon Bedrock

This OWASP agent is a conversational AI assistant designed to help students understand and fix security vulnerabilities, especially those in the [OWASP Top 10](https://owasp.org/www-project-top-ten/). It uses structured prompts and adaptive difficulty levels to generate high-quality educational responses with Node.js code examples.

Powered by **Claude 3.5 (Sonnet)** via **Amazon Bedrock**, this assistant analyzes student questions, identifies security issues, and suggests code-level fixes along with educational follow-ups.

---

## 📌 Features

- ✅ **OWASP Top 10-aware analysis** (SQLi, XSS, CSRF, etc.)
- 🎯 **Difficulty scaling** (1–5) for adaptive learning
- 🧠 **Real-world but student-friendly** explanations
- 📜 **Structured Node.js code examples** (vulnerable & fixed)
- ❓ **Follow-up question suggestions** for deeper learning
- 🔍 Clarifies vague input and handles non-security questions responsibly
- 🤖 Powered by Claude 3.5 via Amazon Bedrock Messages API

---

## 🗂️ Folder Structure

```
project-root/
│
├── agents/
│   └── owasp_agent.py                # OWASP agent logic using Bedrock
│
├── prompts/
│   └── owasp_agent_prompt.txt       # Human-readable prompt template (Claude-style)
│
├── .env                             # Optional: contains MODEL_ID, AWS_REGION
└── README.md                        # This file
```

---

## 🚀 How It Works

### 1. Student asks a security-related question

```text
"Is this login form vulnerable to SQL injection?"
```

### 2. Prompt is built using:

- The question
- A random or specified difficulty level
- A Claude-compatible template with strict response rules

### 3. Model returns:

- Vulnerability analysis
- Insecure and secure Node.js code
- Best practices
- Follow-up learning questions

---

## 🧪 Example Usage

```python
from agents.owasp_agent import handle_owasp_question

response = handle_owasp_question("Show how CSRF works in a contact form.")
print(response)
```

```python
response = handle_owasp_question(
    "Is this Express route safe from XSS?",
    difficulty=4
)
```

---

## 🧠 Prompt Design (Excerpt)

Stored in `prompts/owasp_agent_prompt.txt`, the prompt uses placeholders:

```jinja2
Difficulty level: {{ difficulty_level }}
...
Now analyze the following question:
{{ question }}
```

The model must:

- Identify OWASP category
- Explain the vulnerability clearly
- Include Node.js insecure and secure examples
- Suggest follow-up questions
- Ask if the student wants to go deeper

---

## ⚙️ Environment Variables

| Variable      | Description                         | Default                             |
|---------------|-------------------------------------|-------------------------------------|
| `AWS_REGION`  | AWS region for Bedrock              | `ap-northeast-1`                    |
| `MODEL_ID`    | Claude model ID                     | `anthropic.claude-3-5-sonnet-20240620` |

---

## 📊 Difficulty Levels

| Level | Description               | Sample Topics                              |
|-------|---------------------------|--------------------------------------------|
| 1     | Very Basic                | Reflected XSS, simple SQLi                 |
| 2     | Basic                     | Hardcoded passwords, missing headers       |
| 3     | Moderate                  | Stored XSS, CSRF, weak token logic         |
| 4     | Advanced                  | JWT misuse, IDOR with real-world paths     |
| 5     | Expert                    | Regex DoS, prototype pollution, chaining   |

---

## 🔄 Fallback Logic

If the model determines the question is not related to OWASP:

> “This question may not be related to a security issue. Would you like me to route this to the Assignment assistant?”

---

## 🧱 Suggested Enhancements

- ✅ Streamlit or React frontend integration
- 🔄 Add support for OWASP category detection (e.g., A01, A02...)
- 🧾 DynamoDB logging for learning analytics
- 📘 PDF/HTML report generation for student answers

---

## 📜 License

MIT (or internal use for academic/educational projects)
