import json
import boto3
import os
import traceback

bedrock = boto3.client("bedrock-runtime")

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

def handle_sc_labquiz_gen(question: str, topic: str = "Secure Coding Lab", agent: str = "sc-labquiz-gen") -> dict:
    try:
        prompt = f"""Human: You are a secure coding lab assistant.
Generate 10 multiple-choice questions in JSON format based on the provided lab content. Use the same structure as the few-shot examples.

{FEW_SHOT_EXAMPLES}

Now generate questions based on this lab content:
\"\"\"{question}\"\"\"

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
}}
Assistant:"""

        response = bedrock.invoke_model(
            modelId=os.environ.get("anthropic.claude-v2"),
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 2048
            }),
            accept="application/json",
            contentType="application/json"
        )

        raw_body = response["body"].read().decode("utf-8")
        print("📦 Raw Bedrock Output:", raw_body)

        completion_text = json.loads(raw_body).get("completion", "{}")

        try:
            questions_json = json.loads(completion_text)
        except json.JSONDecodeError as je:
            print("⚠️ Failed to parse model output:")
            print(completion_text)
            raise RuntimeError("Model returned malformed JSON.") from je

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Quiz generated successfully",
                "topic": topic,
                "agent": agent,
                "questions": questions_json.get("questions", [])
            })
        }

    except Exception as e:
        print("❌ Exception while generating quiz:")
        traceback.print_exc()
        raise RuntimeError("❌ Error generating SC Lab Quiz") from e
