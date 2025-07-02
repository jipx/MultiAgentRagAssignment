import json
import boto3
import os
import traceback

bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("DDB_TABLE", "SecureCodingQuizTable")
table = dynamodb.Table(table_name)

FEW_SHOT_EXAMPLES = """
Example 1:
{
  "question": "Which of the following best mitigates SQL injection in a Node.js Express app?",
  "choices": ["Using string concatenation", "Validating input length only", "Parameterized queries", "Disabling logging"],
  "answer": "Parameterized queries",
  "explanation": "Parameterized queries ensure that user input does not interfere with SQL syntax, thus preventing injection attacks."
}

Example 2:
{
  "question": "What is the role of rotating-file-stream in secure logging?",
  "choices": ["Encrypts logs", "Ensures logs are immutable", "Rotates logs periodically", "Sends logs to AWS S3"],
  "answer": "Rotates logs periodically",
  "explanation": "The rotating-file-stream module is used to create a new log file periodically, helping manage log size and prevent log overflow."
}
"""

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        topic = body.get("topic")
        agent = body.get("agent")
        lab_text = body.get("question")

        if not topic or not lab_text:
            raise ValueError("Missing topic or question text.")

        prompt = f"""You are a secure coding lab assistant.
Generate 10 multiple-choice questions in JSON format based on the provided lab content. Use the same structure as the few-shot examples.

{FEW_SHOT_EXAMPLES}

Now generate questions based on this lab content:
\"\"\"
{lab_text}
\"\"\"

Return format:
{{
  "questions": [
    {{
      "question": "...",
      "choices": ["A", "B", "C", "D"],
      "answer": "A",
      "explanation": "..."
    }},
    ...
  ]
}}"""

        response = bedrock.invoke_model(
            modelId=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2"),
            body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 2048}),
            accept="application/json",
            contentType="application/json"
        )

        completion = json.loads(response["body"].read().decode("utf-8"))
        parsed = json.loads(completion.get("completion", "{}"))

        table.put_item(Item={
            "agent": agent,
            "topic": topic,
            "questions": parsed.get("questions", []),
        })

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Quiz saved", "topic": topic, "agent": agent})
        }

    except Exception as e:
        traceback.print_exc()
        raise e  # Raise for SQS retry
