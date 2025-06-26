# 📘 Bedrock Multi-Agent Q&A System

A serverless AI-driven platform for answering student questions on **Assignments** and **OWASP Top 10** using Amazon Bedrock, AWS Lambda, and Streamlit.


## 📚 Features

- Multi-topic support (`assignment`, `owasp`, `assignment+owasp`)
- Bedrock-powered retrieval-augmented responses
- Agent-based routing logic
- Streamlit frontend with:
  - Ask tab
  - History tab
  - Admin dashboard
- Async SQS processing for Bedrock
- DynamoDB storage for response history


## 🏗️ Architecture

```
[Streamlit Frontend]
     |
     v
[API Gateway] --> [Lambda (/ask)]
     |                  |
     |               [SQS]
     |                  |
     |            [Lambda Worker]
     |                  |
     |             [Bedrock Agents]
     |                  |
     |             [DynamoDB Table]
     |
     v
[Lambda (/get-answer)] ← user polls for answer
```


## 🔁 Exception Handling

### 🎯 Objectives

- Avoid saving incomplete or failed responses
- Let SQS retry temporary issues (e.g. throttling)
- Raise errors to trigger DLQ if max retries are reached

### 🔄 Message Flow

| Step | Action                     | Result                      |
|------|----------------------------|-----------------------------|
| 1    | SQS delivers message       | Lambda begins processing    |
| 2    | Bedrock call throttled     | Exception is raised         |
| 3    | Lambda returns error       | Message requeued by SQS     |
| 4    | Retried by SQS             | Reprocessed after delay     |
| 5    | Bedrock responds           | Save to DynamoDB            |


### 🧠 Exception Flowchart

![Exception Handling Flowchart](A_flowchart_titled_%22Exception_Handling_in_AWS_Lamb.png)


## 🧩 Exception Handling Code Snippets

### 🛠 Lambda Worker

```python
def lambda_handler(event, context):
    try:
        for record in event['Records']:
            try:
                message = json.loads(record['body'])
                answer = route_question(message['question'], message['topic'])
                save_answer(
                    table=table,
                    request_id=message['request_id'],
                    user_id=message['user_id'],
                    question=message['question'],
                    answer=answer,
                    timestamp=message.get('timestamp')
                )
            except Exception as e:
                print(f"❌ Error processing message: {str(e)}")
                raise
    except Exception as e:
        print(f"❌ Lambda handler error: {str(e)}")
        raise
```

### 📘 Assignment Agent

```python
def handle_assignment_question(question: str) -> str:
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{model_id}"
                }
            }
        )
        return response["output"]["text"]
    except Exception as e:
        print(f"❌ Bedrock error (Assignment Agent): {e}")
        raise
```

### 🛡 OWASP Agent

```python
def handle_owasp_question(question: str) -> str:
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": owasp_kb_id,
                    "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{owasp_model_id}"
                }
            }
        )
        return response["output"]["text"]
    except Exception as e:
        print(f"❌ Bedrock error (OWASP Agent): {e}")
        raise
```


## 🔧 Environment Variables

| Variable         | Purpose                              |
|------------------|--------------------------------------|
| `MODEL_ID`        | Bedrock model name for assignment    |
| `KB_ID`           | Knowledge base ID for assignment     |
| `OWASP_MODEL_ID`  | Bedrock model ID for OWASP           |
| `OWASP_KB_ID`     | Knowledge base ID for OWASP          |
| `TABLE_NAME`      | DynamoDB table for storing answers   |
| `QUEUE_URL`       | SQS URL for async processing         |


## 🚀 Deployment Checklist

- [x] Configure API Gateway routes for `/ask`, `/get-answer`, `/history`
- [x] Deploy separate Lambdas for ask, answer retrieval, and queue processing
- [x] Set DLQ for SQS and proper visibility timeout
- [x] Use least-privilege IAM roles for:
  - Bedrock model invocation
  - SQS read/write
  - DynamoDB put/get
- [x] Use `.streamlit/secrets.toml` for frontend configuration


## 📂 Project Structure

```
project-root/
├── agents/
│   ├── assignment_agent.py
│   ├── owasp_agent.py
│   └── orchestrator.py
├── lambda_worker/
│   └── lambda_function.py
├── streamlit_app/
│   └── streamlit_app.py
├── utils/
│   └── dynamodb.py
├── .streamlit/
│   └── secrets.toml
├── README.md
```


## 🏁 Summary

This Bedrock-powered multi-agent system ensures robust, retry-safe, and scalable Q&A automation for educational applications using the best of AWS serverless infrastructure.


### OWASP Agent Lambda Exception Handling

```python
import os
import boto3
import botocore.exceptions

owasp_model_id = os.environ["OWASP_MODEL_ID"]
owasp_kb_id = os.environ["OWASP_KB_ID"]
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

def handle_owasp_question(question: str) -> str:
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": owasp_kb_id,
                    "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{owasp_model_id}"
                }
            }
        )
        return response["output"]["text"]

    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']

        if error_code == "ThrottlingException":
            print(f"🚫 Bedrock throttling occurred (OWASP Agent): {error_message}")
        else:
            print(f"❌ Bedrock client error [{error_code}] in OWASP Agent: {error_message}")
        raise

    except Exception as e:
        print(f"❌ Unexpected error in OWASP Agent: {str(e)}")
        raise
```

---

### Assignment Agent Lambda Exception Handling

```python
import os
import boto3
import botocore.exceptions

model_id = os.environ["MODEL_ID"]
kb_id = os.environ["KB_ID"]
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

def handle_assignment_question(question: str) -> str:
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{model_id}"
                }
            }
        )
        return response["output"]["text"]

    except botocore.exceptions.ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']

        if error_code == "ThrottlingException":
            print(f"🚫 Bedrock throttling occurred: {error_message}")
        else:
            print(f"❌ Bedrock client error [{error_code}]: {error_message}")
        raise

    except Exception as e:
        print(f"❌ Unexpected error in Assignment Agent: {str(e)}")
        raise
```

---

### ✅ Unit Tests for Exception Handling

The following `pytest` test cases validate how the Assignment and OWASP agents handle Bedrock throttling exceptions:

```python
import pytest
from unittest.mock import patch, MagicMock
import botocore.exceptions

from agents.assignment_agent import handle_assignment_question
from agents.owasp_agent import handle_owasp_question

def mock_throttling_exception(*args, **kwargs):
    error_response = {
        'Error': {
            'Code': 'ThrottlingException',
            'Message': 'Rate exceeded'
        }
    }
    raise botocore.exceptions.ClientError(error_response, 'retrieve_and_generate')


@patch('agents.assignment_agent.bedrock_runtime.retrieve_and_generate', side_effect=mock_throttling_exception)
def test_assignment_agent_throttling(mock_bedrock):
    with pytest.raises(botocore.exceptions.ClientError) as exc_info:
        handle_assignment_question("When is the assignment due?")
    assert exc_info.value.response['Error']['Code'] == 'ThrottlingException'


@patch('agents.owasp_agent.bedrock_runtime.retrieve_and_generate', side_effect=mock_throttling_exception)
def test_owasp_agent_throttling(mock_bedrock):
    with pytest.raises(botocore.exceptions.ClientError) as exc_info:
        handle_owasp_question("What is OWASP A01?")
    assert exc_info.value.response['Error']['Code'] == 'ThrottlingException'
```

---

### 🧪 Manual Testing in AWS Console

You can also simulate exception handling (e.g. throttling or bad input) directly using the AWS Lambda Console:

#### ✅ Steps to Test Throttling or Error Handling:

1. **Open AWS Console** → Lambda → Select your SQS worker function (e.g., `process-agent-response`).
2. Click **Test** and create a new test event with the following JSON payload:

```json
{
  "Records": [
    {
      "body": "{ \"request_id\": \"test-id-001\", \"user_id\": \"test-student\", \"question\": \"Cause throttling deliberately\", \"topic\": \"assignment\", \"timestamp\": \"2025-10-01T08:00:00Z\" }"
    }
  ]
}
```

3. Ensure the question is something that triggers throttling (or mock it in the agent).
4. Click **Test**. If throttling occurs or a bad model ID is used:
   - The function should **raise an exception**.
   - The message is **not deleted from SQS**.
   - It will **retry** or go to the **DLQ** (if configured).

#### 🔍 Notes:
- Use CloudWatch logs to confirm the error (`ThrottlingException`) and retry behavior.
- You can temporarily modify the agent to always raise `ClientError` for testing.

---

### ❗ Invalid Topic Handling

The `route_question()` function should raise a `ValueError` if a topic is unsupported. This prevents garbage answers from being saved to DynamoDB.

#### ✅ Updated Orchestrator Code:

```python
def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    if topic == "owasp":
        return handle_owasp_question(question)
    elif topic == "assignment":
        return handle_assignment_question(question)
    else:
        raise ValueError(f"❌ Invalid topic received: '{topic}'. No agent available.")
```

#### ✅ Test Case for Invalid Topic:

```python
from agents.orchestrator import route_question
import pytest

def test_invalid_topic_raises():
    with pytest.raises(ValueError) as exc_info:
        route_question("What's the topic?", "unsupported-topic")
    assert "Invalid topic" in str(exc_info.value)
```

---

### 🔁 Updated Orchestrator with Agent Exception Handling

To catch and log any internal exceptions from agents, wrap agent invocations in a `try-except` block:

```python
from agents.owasp_agent import handle_owasp_question
from agents.assignment_agent import handle_assignment_question

def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    try:
        if topic == "owasp":
            return handle_owasp_question(question)
        elif topic == "assignment":
            return handle_assignment_question(question)
        else:
            raise ValueError(f"❌ Invalid topic received: '{topic}'. No agent available.")
    except Exception as e:
        print(f"❌ Error while handling topic '{topic}': {str(e)}")
        raise
```

---

### 🧪 Test Case for Agent Exception Handling

```python
from agents.orchestrator import route_question
import pytest

def test_route_question_with_agent_failure(monkeypatch):
    def fake_assignment_agent(question):
        raise RuntimeError("Simulated internal agent failure")

    monkeypatch.setattr("agents.orchestrator.handle_assignment_question", fake_assignment_agent)

    with pytest.raises(RuntimeError) as exc_info:
        route_question("What is the due date?", "assignment")
    assert "Simulated internal agent failure" in str(exc_info.value)
```

---

### 🪵 Structured Logging with `logging` Module

Replace raw `print()` statements with structured logging for better observability in CloudWatch:

#### ✅ Setup Logging in Lambda

```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
```

#### ✅ Updated Orchestrator Code with Logging

```python
from agents.owasp_agent import handle_owasp_question
from agents.assignment_agent import handle_assignment_question
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def route_question(question: str, topic: str) -> str:
    topic = topic.strip().lower()

    try:
        logger.info(f"🔁 Routing question for topic: '{topic}'")

        if topic == "owasp":
            return handle_owasp_question(question)
        elif topic == "assignment":
            return handle_assignment_question(question)
        else:
            raise ValueError(f"❌ Invalid topic received: '{topic}'")
    except Exception as e:
        logger.error(f"❌ Error handling topic '{topic}': {str(e)}")
        raise
```

#### ✅ Example Lambda Log in CloudWatch

```
🔁 Routing question for topic: 'assignment'
❌ Error handling topic 'assignment': ThrottlingException: Rate exceeded
```

---

### 🧠 Agent-Level Logging

Each agent (Assignment, OWASP) now includes logging for:

- Bedrock API call attempts
- Successful responses
- Throttling or unexpected exceptions

#### ✅ Assignment Agent Logging

```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_assignment_question(question: str) -> str:
    try:
        logger.info("🔍 Calling Bedrock RetrieveAndGenerate for assignment")
        response = bedrock_runtime.retrieve_and_generate(...)
        logger.info("✅ Bedrock response received")
        return response["output"]["text"]
    except botocore.exceptions.ClientError as e:
        ...
        logger.error(f"🚫 Bedrock throttling occurred: {error_message}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in Assignment Agent: {str(e)}")
        raise
```

#### ✅ OWASP Agent Logging

```python
def handle_owasp_question(question: str) -> str:
    try:
        logger.info("🔍 Calling Bedrock RetrieveAndGenerate for OWASP")
        response = bedrock_runtime.retrieve_and_generate(...)
        logger.info("✅ Bedrock response received")
        return response["output"]["text"]
    except botocore.exceptions.ClientError as e:
        ...
        logger.error(f"🚫 Bedrock throttling occurred: {error_message}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in OWASP Agent: {str(e)}")
        raise
```

---

## 📊 Lambda Monitoring in Grafana

You can visualize AWS Lambda performance and logs using Grafana with AWS CloudWatch as a data source.

### ✅ Prerequisites
- Lambda must log to CloudWatch (already handled via `logging` module).
- Lambda role must have `logs:PutLogEvents` and CloudWatch metric permissions.
- Grafana instance must be set up with permission to access CloudWatch.

### 🔧 Steps to Set Up

#### 1. Connect CloudWatch to Grafana
- Go to **Grafana → Configuration → Data Sources → Add Data Source**
- Select **CloudWatch**
- Set region (e.g., `ap-northeast-1`)
- Authenticate with:
  - AWS Access Key (not recommended for production), or
  - Service-linked IAM Role

#### 2. Add a Logs Panel
- **Query Type**: `Logs`
- **Log Group**: `/aws/lambda/YOUR_LAMBDA_NAME`
- **Query Filter**: `? ERROR` or `? ThrottlingException`

#### 3. Add Metrics Panels
You can display:
| Metric       | Namespace     | Dimension     |
|--------------|---------------|---------------|
| Invocations  | AWS/Lambda    | FunctionName  |
| Errors       | AWS/Lambda    | FunctionName  |
| Throttles    | AWS/Lambda    | FunctionName  |
| Duration     | AWS/Lambda    | FunctionName  |

#### 4. Alerts (Optional)
- Set thresholds (e.g., Throttles > 0)
- Use Slack, Email, or SNS for notifications

### 📘 Example Panels
- Line graph of `Throttles` over time
- Table of last 50 log lines with `ERROR` keyword