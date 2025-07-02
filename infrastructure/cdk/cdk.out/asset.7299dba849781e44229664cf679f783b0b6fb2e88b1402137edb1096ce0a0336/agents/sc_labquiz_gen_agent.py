import os
import json
import boto3
import traceback

# Initialize clients
bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

# Few-shot examples to guide Bedrock prompt
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

def handle_sc_labquiz_gen(question: str, topic: str = None) -> str:
    try:
        lab_text = question.strip()

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
            modelId=os.environ.get("MODEL_ID", "anthropic.claude-v2"),
            body=json.dumps({"prompt": prompt, "max_tokens_to_sample": 2048}),
            accept="application/json",
            contentType="application/json"
        )

        body = json.loads(response["body"].read().decode("utf-8"))
        completion_text = body.get("completion", "{}")

        # Validate if it's valid JSON
        questions_json = json.loads(completion_text)

        return questions_json  # Return directly to be stored in DynamoDB by the worker

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError("❌ Error generating SC Lab Quiz") from e
