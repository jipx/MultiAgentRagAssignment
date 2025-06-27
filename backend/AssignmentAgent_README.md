
# 📘 Assignment Agent – README

The **Assignment Agent** is part of the multi-agent Retrieval-Augmented Generation (RAG) system built on Amazon Bedrock. It specializes in handling assignment-related queries using a Bedrock Knowledge Base (KB).

---

## 🧠 Purpose

- Provide context-aware answers to assignment questions.
- Retrieve information from a linked knowledge base (e.g., secure coding rubrics).
- Guide students through follow-up questions to deepen understanding.

---

## 🛠️ Components

### 🔹 Bedrock Foundation Model
- Model ID is configurable (`MODEL_ID` env var).
- Used via RetrieveAndGenerate API.

### 🔹 Knowledge Base (KB)
- Stores documents like PDFs, rubrics, guidelines.
- Queried using Amazon Bedrock's retrieval layer.

### 🔹 Prompt Template
Static prompt file: `prompts/assignment_prompt.txt`

Contains:
```
You are a helpful and concise assistant guiding students on assignment-related topics. 
If a student's question is unclear, ask follow-up questions. 
If the question is assignment-related but touches on OWASP or secure coding, guide them to relevant examples or ask clarification.
Keep responses short and focused.
```

---

## 🔄 Flow

1. User submits a question via `/ask`.
2. If topic is `"assignment"`, the Assignment Agent is selected.
3. `retrieve_and_generate()` is called on Bedrock with:
   - `question`
   - linked `knowledgeBaseId`
   - selected `modelArn`
4. The response is returned to the user and saved to DynamoDB.

---

## 🧩 Agent Fallback Design

If the assignment question is detected to be primarily about OWASP Top 10 (e.g., XSS, SQLi), the agent can:
- Include examples from the KB.
- Ask follow-up questions to confirm context.
- Optionally forward or fall back to the OWASP Agent.

---

## 📁 File Location

```
agents/
├── assignment_agent.py       # Main logic
└── prompts/
    └── assignment_prompt.txt # Prompt used with the foundation model
```

---

## 🧪 Sample Usage

### Sample Input
```json
{
  "question": "How do I fix a SQL injection vulnerability in my assignment?",
  "topic": "assignment"
}
```

### Sample Output
> SQL injection occurs when untrusted input is used directly in SQL queries. To fix it, use parameterized queries or ORM methods. Would you like to see an example of a fixed code snippet?

---

## ✅ Environment Variables

| Variable      | Description                          |
|---------------|--------------------------------------|
| `MODEL_ID`    | Bedrock model ID (e.g., Claude V2)   |
| `KB_ID`       | Bedrock Knowledge Base ID            |
| `AWS_REGION`  | Region where Bedrock is hosted       |

---

## 🔒 IAM Permissions Required

- `bedrock:InvokeModel`
- `bedrock:Retrieve`
- `bedrock:RetrieveAndGenerate`

These must be granted to the Lambda's execution role.

