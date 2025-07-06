# 🔧 Adding LabHint and CodeReview Agents to Your Backend
This guide walks you through integrating two new agents — **LabHint** and **CodeReview** — into your AWS Lambda-based Bedrock QA system.

## 📁 1. Create Prompt Templates
Create two files under `prompts/`:

### `prompts/labhint.txt`
```
You are a Lab Hint Assistant helping students with secure coding lab exercises...
Lab Context:
{{ lab_notes }}

Student Question:
{{ student_question }}
```

### `prompts/codereview.txt`
```
You are a secure coding review assistant...
Student Question (includes code snippet and context):
{{ student_question_with_code }}
```

## 🧠 2. Implement Agent Logic
Create two new agent handlers under `agents/`:

### `agents/labhint_agent.py`
```python
from utils import load_prompt_template, call_bedrock_model

def handle_labhint(lab_notes, student_question):
    prompt = load_prompt_template("prompts/labhint.txt")
    filled_prompt = prompt.replace("{{ lab_notes }}", lab_notes).replace("{{ student_question }}", student_question)
    return call_bedrock_model(filled_prompt)
```

### `agents/codereview_agent.py`
```python
from utils import load_prompt_template, call_bedrock_model

def handle_codereview(student_question_with_code):
    prompt = load_prompt_template("prompts/codereview.txt")
    filled_prompt = prompt.replace("{{ student_question_with_code }}", student_question_with_code)
    return call_bedrock_model(filled_prompt)
```

## 🔁 3. Register in `orchestrator.py`
Update your routing logic:

```python
from agents.labhint_agent import handle_labhint
from agents.codereview_agent import handle_codereview

def route_question(topic, message):
    if topic == "labhint":
        return handle_labhint(message.get("lab_notes", ""), message.get("student_question", ""))
    elif topic == "codereview":
        return handle_codereview(message.get("student_question_with_code", ""))
    # ... other topics
```

## ⚙️ 4. Update `lambda_worker.py`
```python
topic = body.get("topic", "assignment")
try:
    answer = route_question(topic, body)
    # save to DynamoDB or return result
except Exception as e:
    logger.error(f"Error handling topic '{topic}': {e}")
```

## 🧪 5. Test Payloads

### LabHint
```json
{
  "topic": "labhint",
  "lab_notes": "Use parameterized queries to avoid SQL injection when storing comments.",
  "student_question": "Can I just concatenate the user input into the SQL query string?"
}
```

### CodeReview
```json
{
  "topic": "codereview",
  "student_question_with_code": "app.post('/login', (req, res) => { const u = req.body.user; const p = req.body.pass; db.query(`SELECT * FROM users WHERE username = '${u}' AND password = '${p}'`); });"
}
```

## 📦 6. Folder Structure
```
backend/
├── lambda_worker/
│   ├── lambda_function.py
│   ├── orchestrator.py
│   └── utils.py
├── agents/
│   ├── labhint_agent.py
│   └── codereview_agent.py
├── prompts/
│   ├── labhint.txt
│   └── codereview.txt
```

## ✅ Next Steps
- [ ] Add unit tests for each agent
- [ ] Add to CI/CD deployment (CDK, Terraform, etc.)
- [ ] Enable monitoring/logs for new topics in CloudWatch
- [ ] Expose new agents via API Gateway if needed
