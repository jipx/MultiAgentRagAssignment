
# 📚 Assignment Knowledge Base (KB) – Setup & Integration Guide

This guide outlines how to create and connect a document-based **Knowledge Base (KB)** in **Amazon Bedrock** for assignment-related queries in a multi-agent RAG system.

---

## 🧠 What Is a KB?

A **Knowledge Base** in Amazon Bedrock allows you to ground foundation model responses in **your own documents** (e.g., PDFs, markdown, text) using retrieval-augmented generation (RAG).

---

## 📁 Step-by-Step KB Setup

### 1. 📄 Prepare Your Documents

Upload assignment resources like:
- Assignment brief
- Rubrics
- Sample answers
- Secure coding checklists

Recommended formats: `.pdf`, `.txt`, `.md`, `.html`

---

### 2. 🪣 Upload to S3

Create a folder in your bucket:

```bash
s3://bedrock-kb/assignments/secure-coding/
```

Upload your documents into this S3 path.

---

### 3. 🧠 Create the Knowledge Base in Bedrock Console

Navigate to **Amazon Bedrock → Knowledge bases → Create knowledge base**:

- **Name**: `assignment-kb`
- **S3 URI**: `s3://bedrock-kb/assignments/secure-coding/`
- **Embedding model**: `Amazon Titan Embeddings G1`
- **Vector store**: `Amazon OpenSearch Serverless` (create new if needed)

Choose the **retriever** and **chunking** settings (default is OK for small docs).

---

### 4. 🧪 Test in Console

Use the **chat window** in Bedrock KB console to validate grounding. Try:

> “When is the secure coding assignment due?”

---

## 🔌 Connect to Lambda Orchestrator

### 5. Set Environment Variable in CDK or Manually

```json
{
  "KB_ID": "assignment-kb-abc123"
}
```

In your Lambda function (e.g., `assignment_agent.py`), make sure you retrieve this value:

```python
import os

KB_ID = os.environ['KB_ID']
```

---

### 6. Code Example – Querying Bedrock with KB

```python
import boto3

bedrock_agent = boto3.client('bedrock-agent-runtime')

def query_assignment_kb(question):
    response = bedrock_agent.retrieve_and_generate(
        input={
            "input": {
                "text": question
            }
        },
        knowledgeBaseId=os.environ['KB_ID']
    )
    return response['output']['text']
```

---

## 🧪 Sample SQS Message from API Gateway → SubmitLambda → SQS

```json
{
  "question_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "student001",
  "question": "When is the secure coding assignment due?",
  "topic": "assignment",
  "timestamp": "2025-10-01T08:00:00Z"
}
```

This is routed by the orchestrator to the assignment agent, which calls the Bedrock KB.

---

## 🛠️ Troubleshooting

| Issue | Cause | Fix |
|------|-------|-----|
| `AccessDeniedException` | Missing permissions for Bedrock | Add `bedrock:*` for `bedrock-agent-runtime` |
| `InvalidKnowledgeBaseId` | Wrong `KB_ID` | Check env vars and Bedrock console |
| No KB responses | Chunking or embedding failed | Re-upload documents and re-index |
| Empty response | Question not grounded well | Rephrase question or review documents |

---

## ✅ AWS Best Practices for KB

- 🔐 Use **least-privilege IAM roles** for Lambda (only allow `RetrieveAndGenerate`)
- 🧠 Use **Titan Embeddings** for cost-effective semantic search
- 🧾 Keep documents small and cleanly chunked (avoid large tables/images)
- 💾 Enable versioning in S3 for auditing document changes
- 🔁 Re-ingest documents regularly if updates are made
