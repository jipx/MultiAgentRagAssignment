# 📚 Assignment Q&A Agent using Amazon Bedrock Knowledge Base

This project deploys a fast, accurate, and grounded **Assignment Assistant** on AWS Lambda using **Amazon Bedrock Knowledge Base (KB)** and **Titan Text Express**.

It allows students to ask natural language questions about assignment deadlines, submission instructions, rubrics, and requirements. The answers are generated based on your own curated documents (PDFs, Markdown, etc.) ingested into a Bedrock KB.

---

## 🚀 Features

- ✅ Serverless Lambda using Bedrock Knowledge Base
- ⚡ Fast generation using Titan Text Express
- 📎 Accurate answers grounded in your uploaded documents
- 🧬 Embedded vector search using Titan Embeddings
- 🔐 IAM secure API access

---

## 🧪 Example Questions

- *When is the secure coding assignment due?*
- *How do I submit the database assignment?*
- *What are the grading criteria?*
- *Can I submit after the deadline?*

---

## 📁 Folder Structure

```
assignment_agent_lambda/
├── lambda_function.py
├── utils/
│   └── retrieval.py
│   └── prompt_templates.py
```

---

## 🛠️ Setup Instructions

### 1. Create a Knowledge Base

- In the AWS Console > Amazon Bedrock > Knowledge Bases
- Upload assignment documents (PDF, DOCX, TXT, Markdown)
- Choose **Titan Embeddings**: `amazon.titan-embed-text-v1`
- Name your KB and note the `knowledgeBaseId`

### 2. Deploy Lambda

Set up a Lambda function using `lambda_function.py`. Add environment variables:

- `KNOWLEDGE_BASE_ID`: your KB’s ID
- `MODEL_ARN`: e.g. `arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1`

### 3. Add IAM Permissions

Attach this to your Lambda role:

```json
{
  "Effect": "Allow",
  "Action": "bedrock-agent:RetrieveAndGenerate",
  "Resource": "*"
}
```

---

## 📥 Sample Input

```json
{
  "question": "How do I submit the secure coding assignment?"
}
```

## 📤 Sample Output

```json
{
  "question": "How do I submit the secure coding assignment?",
  "answer": "You must submit it via Moodle before Sept 20, 11:59 PM using the PDF upload link."
}
```

---

## 🔄 End-to-End Flow

### 🔁 Assignment Agent Runtime Flow

```
[Student Question]
     ↓
[Lambda → retrieve_and_generate()]
     ↓
[Retrieve: vector search in KB]
     ↓
[Generate: Titan Text Express]
     ↓
[Return grounded answer]
```

---

### 🧬 Embeddings Flow

#### 📥 When Creating Knowledge Base

```
Documents → Chunked → Embedded (Titan) → Vector DB
```

- Embeddings are only created **once** during ingestion
- Uses `amazon.titan-embed-text-v1`

#### 🤖 When Answering Questions

```
Question → Embedded (Titan) → Match vectors → Generate with Titan Text Express
```

- Same embedding model used for matching (automatically handled)
- Generation model (e.g., `titan-text-express-v1`) specified at runtime

---

## ⚡ Recommended Models for Speed

| Use Case       | Model                           | ARN |
|----------------|----------------------------------|-----|
| Fast Q&A       | `amazon.titan-text-express-v1`  | `arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1` |

---

## 🧠 Notes

- **Embeddings and generation are separate.**
  - Embeddings = used to index and search your KB.
  - Generation = used to create natural language answers.
- The embedding model is fixed at KB creation.
- The generation model ARN is chosen per API call.

---

## 📅 Last updated: June 28, 2025


---

## ✨ Prompt Design & Tuning Guide

While Amazon Bedrock handles grounding via its Knowledge Base, the way you **frame the prompt** for the language model still affects the final output clarity and accuracy.

### ✅ Best Practice Prompt Template

```text
You are a helpful academic assistant. Answer student questions using only the information in the provided assignment context.

If the answer is not in the context, respond with:
"I don’t know. Please check the official assignment brief or ask your instructor."

Context:
{{retrieved_context}}

Student Question:
{{user_question}}

Answer:
```

- This prompt is automatically handled internally by Bedrock KB unless you're using a custom orchestration layer.
- You can override this format using `promptOverrideConfiguration` in advanced use cases.

---

## 🧪 Prompt Testing Strategies

Use a range of test questions to evaluate the reliability of the agent:

| Test Type       | Sample Question                                 | Expectation                           |
|------------------|--------------------------------------------------|----------------------------------------|
| ✅ Factual match  | *When is the secure coding assignment due?*     | Correct date, grounded in KB           |
| ⚠️ Not in KB      | *Can I submit via email?*                      | "I don’t know" or clarification needed |
| ✅ Rubric query   | *How are marks awarded?*                        | Bullet list or rubric description      |
| ⚠️ Ambiguous      | *What do I do?*                                | Ask for clarification or return N/A    |
| ✅ Submission     | *Where do I upload my assignment?*              | "Moodle", "Turnitin", etc.             |

> Use CloudWatch Logs to inspect returned answers for various test questions. Ensure responses are grounded in your KB documents and that irrelevant queries fail gracefully.

---

## 🧰 Advanced Prompt Overrides (Optional)

If you implement your own Bedrock orchestration (e.g., with LangChain or Prompt Engineering), you can:

- Add step-by-step reasoning
- Format the response as JSON or Markdown
- Include confidence levels

Example advanced prompt:

```text
You are an AI tutor. Use ONLY the context provided below. Show reasoning if applicable. If unsure, say "I don’t know."

Context:
{{retrieved_context}}

Question:
{{user_question}}

Answer (with reasoning):
```

---
