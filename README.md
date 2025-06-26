# 🧠 Bedrock Multi-Agent RAG System

This project implements a **Retrieval-Augmented Generation (RAG)** system using multiple agents and Amazon Bedrock. It supports structured Lambda-based orchestration, integrates a Bedrock knowledge base (KB), and is deployable with AWS CDK.

---

## 🗂️ Features

- Multiple agents: OWASP, Assignment, Classifier
- Secure architecture with IAM roles and SQS DLQ
- Assignment knowledge base (KB) for document-grounded responses
- REST API endpoints via API Gateway
- Lambda-to-Lambda orchestration for task separation
- DynamoDB for persistence
- Load-tested and throttled API configurations

---

## 🏗️ Project Architecture



### 🔧 Components
- **API Gateway** – Handles RESTful endpoints:
  - `POST /ask` to submit a question
  - `GET /get-answer` to fetch a specific answer
  - `GET /history` to retrieve a user's Q&A history
- **Submit Lambda** – Validates and pushes questions to an SQS queue.
- **SQS Queue** – Buffers incoming question jobs.
- **Worker Lambda** – Polls the SQS queue, routes to the correct agent via the orchestrator, queries Bedrock FM + KB, and saves answers to DynamoDB.
- **DynamoDB** – Stores questions, answers, timestamps, and user context.
- **GetAnswer & GetHistory Lambdas** – Query DynamoDB for specific or historical results.
- **Agents (Orchestrator)** – Decide routing based on topic (e.g., OWASP, Assignment).
- **Amazon Bedrock** – Foundation Models used for answering and classifying questions.
- **Knowledge Base** – Assignment-related documents embedded and indexed for RAG context.

### 🗺️ Flow Overview
```text
User ➝ API Gateway ➝ Submit Lambda ➝ SQS ➝ Worker Lambda ➝ Orchestrator ➝ Agent ➝ Bedrock (with KB)
                                                                  ⤷ DynamoDB (save result)
User ➝ API Gateway ➝ GetAnswer / GetHistory ➝ DynamoDB
```

---

## 📦 Project Structure

```
backend/
│
├── lambda_submit/        # Receives API input and submits to SQS
├── lambda_worker/        # Consumes SQS, routes to orchestrator, saves to DynamoDB
├── lambda_get_answer/    # Retrieves individual result
├── lambda_get_history/   # Retrieves all results for user
│
├── agents/               # Agent logic (owasp_agent.py, assignment_agent.py)
└── utils/                # DynamoDB helpers
```

---

## 🚀 API Endpoints

| Endpoint         | Method | Description                      |
|------------------|--------|----------------------------------|
| `/ask`           | POST   | Submits a question               |
| `/get-answer`    | GET    | Retrieves answer by request_id   |
| `/history`       | GET    | Retrieves full history for user  |

### Sample Request to `/ask`
```json
{
  "user_id": "student001",
  "question": "When is the secure coding assignment due?",
  "topic": "assignment"
}
```

---

## 📨 Message Formats

### 🔄 API Gateway → Submit Lambda
API Gateway passes a Lambda Proxy Integration format:
```json
{
  "resource": "/ask",
  "path": "/ask",
  "httpMethod": "POST",
  "body": "{"question": "What is XSS?", "user_id": "user-123", "topic": "owasp"}",
  "isBase64Encoded": false
}
```

**Submit Lambda parses it using:**
```python
body = json.loads(event.get("body") or '{}')
question = body.get("question")
user_id = body.get("user_id")
topic = body.get("topic")
```

---

### 📤 Lambda → SQS
Submit Lambda sends:
```json
{
  "question_id": "3fc9d93e-44de-4a10-88dc-9a7bd74f3cbe",
  "user_id": "user-123",
  "question": "What is SQL injection?",
  "topic": "owasp",
  "timestamp": "2025-06-24T10:00:00Z"
}
```
Using:
```python
sqs.send_message(
  QueueUrl=QUEUE_URL,
  MessageBody=json.dumps(message)
)
```

---

### 📥 SQS → Worker Lambda
SQS event contains:
```json
{
  "Records": [
    {
      "body": "{ "question_id": "3fc9d93e-44de-4a10-88dc-9a7bd74f3cbe", "user_id": "user-123", "question": "What is SQL injection?", "topic": "owasp", "timestamp": "2025-06-24T10:00:00Z" }"
    }
  ]
}
```

**Worker Lambda parses it with:**
```python
for record in event['Records']:
    message = json.loads(record['body'])
```

---

## 🧠 Setting Up Assignment Knowledge Base in Bedrock

1. Upload assignment files to S3: `s3://your-kb-bucket/assignments/`
2. Create a Bedrock KB with Titan Embeddings + OpenSearch
3. Use KB ID in Lambda as an environment variable: `KB_ID=assignment-kb-001`

---

## 🧪 Testing and Load Simulation

### ✅ Postman
POST to `/ask` with:
```json
{
  "user_id": "test001",
  "question": "What is XSS?",
  "topic": "owasp"
}
```

### ✅ Python Load Test
```python
import requests, uuid
from datetime import datetime

for i in range(10):
    payload = {
        "user_id": "loadtest",
        "question": f"What is test {i}?",
        "topic": "owasp",
        "timestamp": datetime.utcnow().isoformat()
    }
    res = requests.post("https://<api-id>.execute-api.<region>.amazonaws.com/prod/ask", json=payload)
    print(i, res.status_code)
```

---

## 🚨 Troubleshooting

| Issue                         | Cause / Fix                                           |
|------------------------------|--------------------------------------------------------|
| 400 Bad Request              | Check for missing `question`, `user_id`, or `topic`   |
| 500 Internal Server Error    | Check Lambda logs (CloudWatch) for stack trace        |
| Message not processed        | See DLQ; check retry count, Lambda timeout, etc.      |
| No response from `/get-answer` | May not be processed yet; check `request_id`         |

---

## ✅ AWS Best Practices (Detailed)

- 🔐 Least-privilege IAM roles per Lambda
- 🧱 SQS with DLQ to capture failed jobs
- 📊 CloudWatch alarms for DLQ usage
- 💡 API Gateway throttling enabled
- 🧼 Retry-safe Lambdas with structured error handling
- 💾 Pay-per-request DynamoDB mode for cost efficiency