# Bedrock RAG Multi-Agent System

This project implements a serverless multi-agent Retrieval-Augmented Generation (RAG) system using Amazon Bedrock, AWS Lambda, API Gateway, SQS, and DynamoDB. Each agent specializes in a different domain (e.g., OWASP, Secure Coding) and responds to user questions asynchronously.

---

## 📁 Project Structure

```
.
├── backend/
│   ├── lambda_submit/         # Accepts questions and queues them
│   ├── lambda_worker/         # Processes questions using Bedrock agents
│   ├── lambda_get_answer/     # Retrieves a single answer from DynamoDB
│   └── lambda_get_history/    # Retrieves answer history from DynamoDB
├── infrastructure/
│   └── cdk/
│       ├── app.py             # CDK entry point
│       ├── multiagent_stack.py# CDK Stack definition
│       ├── cdk.json           # CDK configuration
│       └── cdk.context.json   # Runtime config: model ID, endpoint, etc.
├── cdk_requirements.txt       # CDK dependencies
└── README.md
```

---

## 🛠 Setup Instructions

### 1. 📦 Create and Activate Virtual Environment

```bash
cd infrastructure/cdk
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate    # Linux/Mac
```

### 2. 📥 Install CDK Dependencies

```bash
pip install -r ../../cdk_requirements.txt
```

> Make sure your `cdk_requirements.txt` includes:
```txt
aws-cdk-lib==2.128.0
constructs>=10.0.0,<11.0.0
```

---

## 🚀 Deploy the Stack

### Bootstrap your AWS account:
```bash
cdk bootstrap aws://628902727523/ap-southeast-1
```

### Deploy:
```bash
cdk deploy
```

---

## 🌐 API Endpoints

Once deployed, you’ll get a URL like:

```
https://xyz123.execute-api.ap-southeast-1.amazonaws.com/prod
```

| Method | Endpoint       | Description                         |
|--------|----------------|-------------------------------------|
| POST   | `/ask`         | Submit a question to SQS            |
| GET    | `/get-answer`  | Get the answer using request_id     |
| GET    | `/history`     | Retrieve all previous Q&A           |

---

## 🧠 Environment Context

Defined in `cdk.context.json`:

```json
{
  "model_name": "Claude",
  "model_id": "anthropic.claude-v2",
  "kb_id": "owasp-kb-001",
  "rag_endpoint_url": "https://bedrock-runtime.ap-southeast-1.amazonaws.com"
}
```

---

## 🔒 Security & Monitoring

- All Lambdas use least privilege IAM roles.
- DLQ with CloudWatch alarm monitors failed messages.
- Environment variables securely pass model config to worker functions.

---

## 🧪 Testing Lambda Functions via AWS Console

### SubmitLambda
```json
{
  "body": "{\"question\": \"What is SQL Injection?\", \"course\": \"owasp\"}"
}
```

### WorkerLambda (SQS Event)
```json
{
  "Records": [
    {
      "body": "{\"request_id\": \"abc-123\", \"question\": \"Explain XSS\", \"course\": \"owasp\"}"
    }
  ]
}
```

### GetAnswerLambda
```json
{
  "queryStringParameters": {
    "request_id": "abc-123"
  }
}
```

### GetHistoryLambda
```json
{
  "queryStringParameters": {
    "course": "owasp"
  }
}
```

---

## 🌐 Testing API Gateway via Console or Postman

### POST /ask
**URL:**  
`https://<api-id>.execute-api.ap-southeast-1.amazonaws.com/prod/ask`  
**Method:** POST  
**Body:**
```json
{
  "question": "What is SSRF?",
  "course": "owasp"
}
```

### GET /get-answer
`https://<api-id>.execute-api.ap-southeast-1.amazonaws.com/prod/get-answer?request_id=abc-123`

### GET /history
`https://<api-id>.execute-api.ap-southeast-1.amazonaws.com/prod/history?course=owasp`

---

## 📬 Contact

For support, contact: `pengx@example.com`


---

## 🧠 OWASP Agent Prompt Template

The following prompt is used by the OWASP agent in the Lambda worker to generate high-quality, structured answers from Bedrock:

```
You are a cybersecurity expert specializing in web application vulnerabilities based on the OWASP Top 10 framework. Your task is to answer questions related to secure coding, vulnerability types, exploitation methods, and remediation best practices.

Context:
- Focus on OWASP categories such as A01:2021 – Broken Access Control, A03:2021 – Injection, A07:2021 – Identification and Authentication Failures, and so on.
- Include real-world examples or analogies when possible.
- Explain both the attack vector and the mitigation strategy clearly.
- If the user question is vague, infer the intent and provide a useful answer.

Format your response with:
1. **Summary** (1-2 lines)
2. **Technical Explanation**
3. **Example**
4. **Remediation Guidance**
5. **References or Further Reading** (optional)

Respond only in English. Keep the tone professional but student-friendly.
```

This prompt is passed to Bedrock when invoking the OWASP agent in `lambda_worker/lambda_function.py`.


---

## 🤖 Additional Agent Prompt Templates

### 🔐 Secure Coding Agent
```
You are a senior software engineer and secure coding trainer. Your task is to help developers write secure applications by explaining vulnerabilities and providing code-level guidance.

Context:
- Focus on best practices in input validation, authentication, authorization, and safe API usage.
- Cover common flaws like SQL Injection, XSS, Insecure Deserialization, etc.
- Provide guidance in popular languages like JavaScript, Python, and Java.

Structure your response:
1. **Issue Summary**
2. **Why It Happens**
3. **Insecure Code Example**
4. **Secure Code Example**
5. **Mitigation Tips**
```

---

### 🧮 Database Agent
```
You are a database administrator and trainer. Your role is to help users understand how to design, query, and secure databases.

Context:
- Focus on normalization, indexing, SQL performance, transaction safety, and access control.
- Explain query optimization, data integrity, and pitfalls in relational and NoSQL models.

Format:
1. **Concept Overview**
2. **Example Schema/Query**
3. **Best Practices**
4. **Performance or Security Tips**
```

---

### 🤖 AI & Machine Learning Agent
```
You are an AI engineer with experience in model development, prompt engineering, and MLOps.

Context:
- Answer questions on supervised learning, transformers, prompt design, bias mitigation, and ethical AI.
- Offer tips on fine-tuning, evaluation, and securing ML pipelines on cloud platforms.

Structure:
1. **Concept Summary**
2. **Technical Deep Dive**
3. **Real-World Example**
4. **Caveats or Pitfalls**
5. **Resources to Learn More**
```


---

## 🤖 Automatic Agent Classification

If the user does not specify a course (agent), the system uses a classifier prompt to automatically infer the correct agent based on the question.

### 🔍 How it Works

When a user submits a question like:
```
What is the due date for the secure coding assignment?
```

The system sends the following prompt to Bedrock:
```
You are a classification assistant. Your task is to classify the following question into one of these categories:
- owasp
- securecoding
- dbs
- ai

Respond with only the category name.

Question: What is the due date for the secure coding assignment?
Answer:
```

The result is used to route the question to the correct agent.

### 🧠 Examples

| Question                                                | Routed Agent    |
|---------------------------------------------------------|-----------------|
| What is SQL Injection?                                  | owasp           |
| When is the secure coding assignment due?               | securecoding    |
| How to normalize a relational database?                 | dbs             |
| What is fine-tuning in machine learning?                | ai              |

This ensures users can ask questions naturally without needing to select a category.


---

## 🧪 Sample Questions Per Agent

Use these questions to test each domain-specific agent.

### 🔐 OWASP Agent
1. What is SQL Injection and how can it be prevented?
2. How does Cross-Site Scripting work?
3. What are examples of Broken Access Control?
4. Explain the risk of insecure deserialization.
5. What is the difference between authentication and authorization?

### 🛡️ Secure Coding Agent
1. How do I validate user input in Python?
2. What's the secure way to handle passwords in Node.js?
3. How can I prevent hardcoded credentials in my app?
4. What is a secure pattern for file uploads?
5. How do I use parameterized queries in Java?

### 🧮 Database Agent
1. How do I normalize a database to 3NF?
2. What are common indexing strategies in PostgreSQL?
3. Explain ACID properties in databases.
4. How do I optimize a slow SQL JOIN?
5. What is the difference between a primary key and a foreign key?

### 🤖 AI & Machine Learning Agent
1. What is the difference between supervised and unsupervised learning?
2. How does a transformer model work?
3. What is prompt engineering in LLMs?
4. How can I detect bias in a machine learning model?
5. What is MLOps and why is it important?

These questions help test classification, prompt structure, and answer relevance.


---

## 🧰 Troubleshooting Guide

### ❌ CDK Error: `Cannot find asset at lambda_submit`
**Cause:** File path in CDK doesn't match actual directory structure.

**Fix:** Ensure `lambda_submit/`, `lambda_worker/`, etc. exist under `infrastructure/cdk/backend/` or correct the path in `multiagent_stack.py`.

---

### ❌ CDK Error: `Unsupported feature flag '@aws-cdk/core:enableStackNameDuplicates'`
**Cause:** Legacy CDK v1 flag no longer supported in CDK v2.

**Fix:** Ensure you're using `aws-cdk-lib` and not importing `core`:
```python
# ✅ Correct for CDK v2
import aws_cdk as cdk
```

---

### ❌ Lambda Error: `ModuleNotFoundError: No module named 'aws_cdk.aws_certificatemanager'`
**Cause:** Missing CDK module during synthesis.

**Fix:** Add missing dependency in `cdk_requirements.txt`:
```txt
aws-cdk-lib==2.128.0
constructs>=10.0.0,<11.0.0
```

---

### ❌ ENOENT: `cdk.out/manifest.json` missing
**Cause:** CDK failed to synthesize due to prior error.

**Fix:** Resolve syntax or dependency issues, then re-run:
```bash
cdk synth
```

---

### ❌ API Returns 500 Internal Server Error
**Cause:** Likely unhandled error in Lambda or Bedrock response.

**Fix:**
- Check CloudWatch logs for your Lambda.
- Ensure prompt formatting is valid.
- Validate environment variables (e.g., `rag_endpoint_url`, `model_id`).

---

### ❌ No answer returned for question
**Fix:**
- Make sure `worker` Lambda has permission to call Bedrock.
- Check DynamoDB write logic.
- Confirm valid response format from the model.

---

For any other issues, check:
- CloudWatch Logs
- IAM Role permissions
- API Gateway logs


---

## ✅ Alignment with AWS Best Practices

This project aligns with the [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) across the following pillars:

### 🛡️ Security
- **Least Privilege IAM Roles**: Each Lambda function uses a dedicated IAM role with the minimum permissions required.
- **Environment Variables**: Secure handling of runtime config like model IDs and endpoints.
- **API Gateway**: Can be extended with Cognito or API Key-based access control.
- **SQS Dead Letter Queue**: Captures failed messages and enables retry logic.
- **CloudWatch Logs**: Automatically enabled for all Lambda functions.

### ⚙️ Operational Excellence
- **CDK Infrastructure as Code**: Enables reproducible deployments and version control.
- **Logging & Monitoring**: CloudWatch captures invocation logs and errors for observability.
- **Environment Separation**: Supports deploying to multiple environments via CDK context.

### 🔄 Reliability
- **SQS Queue**: Buffers requests to decouple front-end from back-end processing.
- **DLQ (Dead Letter Queue)**: Prevents message loss during processing failures.
- **Retry Logic**: SQS and Lambda retry policies can be configured as needed.

### 💰 Cost Optimization
- **Serverless Architecture**: Uses Lambda and API Gateway with pay-per-use pricing.
- **DynamoDB On-Demand**: Avoids overprovisioning and scales based on traffic.
- **No EC2 or container overhead**: Reduces infrastructure management and idle cost.

### 🚀 Performance Efficiency
- **Bedrock API**: Scalable and low-latency generative AI via managed API.
- **Asynchronous processing**: Ensures frontend responsiveness while backend computes answers.
- **API Gateway caching** *(optional)*: Can be enabled to reduce latency for frequent requests.

---

To further align with AWS best practices, consider:
- Adding throttling and rate limiting to API Gateway.
- Using AWS Secrets Manager for sensitive values.
- Adding alarms for failed invocations and SQS backlog thresholds.


---

## ⏱️ Tuning Timeouts for SQS and Lambda

Proper timeout configuration is essential to ensure reliable message processing and prevent duplicate or failed executions.

### 🔁 SQS Visibility Timeout

**Purpose:** The visibility timeout determines how long a message stays hidden after a worker begins processing it.

**Best Practice:**
- Set the visibility timeout slightly longer than the expected maximum Lambda processing time.

> Example:
> If your Lambda may take up to 15 seconds, set the visibility timeout to **20–30 seconds**.

```python
rag_queue = sqs.Queue(
    self, "RAGQueue",
    visibility_timeout=Duration.seconds(30)
)
```

---

### ⌛ Lambda Function Timeout

**Purpose:** Lambda timeout defines how long AWS will wait before forcibly terminating the function.

**Best Practice:**
- Set this based on the complexity of the Bedrock generation task.
- For typical Bedrock prompts, 10–30 seconds is recommended.

```python
_lambda.Function(
    self, "WorkerLambda",
    timeout=Duration.seconds(30),
    ...
)
```

---

### ✅ Summary

| Component | Timeout Setting      | Suggested Value  |
|-----------|----------------------|------------------|
| SQS       | `visibility_timeout` | 30 seconds       |
| Lambda    | `timeout`            | 30 seconds       |

Adjust based on testing for longer responses or heavier models (e.g., Claude v2). Always ensure SQS timeout > Lambda timeout to avoid duplicate processing.


---

## 🛠️ Setting Timeouts in CDK (Best Practice)

Use these code snippets to configure timeouts for SQS and Lambda based on AWS best practices.

### ⏱️ 1. Set Lambda Timeout

Set the maximum execution time for your Lambda function (e.g., 30 seconds):

```python
worker_lambda = _lambda.Function(
    self, "WorkerLambda",
    runtime=_lambda.Runtime.PYTHON_3_12,
    handler="lambda_function.handler",
    code=_lambda.Code.from_asset("backend/lambda_worker"),
    timeout=Duration.seconds(30),
    environment={
        "ANSWER_TABLE": answer_table.table_name,
        "MODEL_NAME": context["model_name"],
        "MODEL_ID": context["model_id"],
        "KB_ID": context["kb_id"],
        "BEDROCK_ENDPOINT_URL": context["rag_endpoint_url"]
    }
)
```

---

### 🔁 2. Set SQS Visibility Timeout (Longer than Lambda)

Ensure the visibility timeout is longer than the Lambda timeout (e.g., 35 seconds):

```python
rag_queue = sqs.Queue(
    self, "RAGQueue",
    visibility_timeout=Duration.seconds(35)
)
```

---

### 🚨 3. Add Dead Letter Queue (Optional)

To avoid infinite retry loops for failed messages:

```python
dlq = sqs.Queue(self, "RAGDLQ")

rag_queue = sqs.Queue(
    self, "RAGQueue",
    visibility_timeout=Duration.seconds(35),
    dead_letter_queue=sqs.DeadLetterQueue(
        max_receive_count=3,
        queue=dlq
    )
)
```

---

### ✅ Summary

| Component | Timeout Setting      | Suggested Value  |
|-----------|----------------------|------------------|
| Lambda    | `timeout`            | 30 seconds       |
| SQS       | `visibility_timeout` | 35 seconds       |
| DLQ       | `max_receive_count`  | 3                |

This configuration ensures reliability, avoids duplicate processing, and supports fault recovery.

