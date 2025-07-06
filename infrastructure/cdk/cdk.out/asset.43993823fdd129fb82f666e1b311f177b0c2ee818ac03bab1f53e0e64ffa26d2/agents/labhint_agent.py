import json
import boto3
import os
import traceback

bedrock = boto3.client("bedrock-runtime")

FEW_SHOT_HINTS = """
Example 1:
{
  "task": "Sanitize user input to prevent XSS.",
  "hint": "Consider using a well-known library like DOMPurify or applying strict input validation with a whitelist approach."
}

Example 2:
{
  "task": "Log user activity securely using Winston.",
  "hint": "Think about log rotation, timestamps, and ensuring no sensitive data is logged."
}
"""

def run_labhint_agent(task: str, labnotes: str = "", topic: str = "Secure Coding Lab", agent: str = "labhints") -> dict:
    try:
        messages = [
            {
                "role": "user",
                "content": f"""You are a helpful assistant for secure coding lab students.

Your job is to give clear, concise **hints** (not solutions) to help them complete lab tasks. Do not reveal any answer directly. Use the lab context and examples to craft your response.

Lab notes:
\"\"\"{labnotes}\"\"\"

{FEW_SHOT_HINTS}

Now provide a helpful hint for this lab task:
\"\"\"{task}\"\"\"

Return format:
{{
  "hint": "..."
}}
"""
            }
        ]

        response = bedrock.invoke_model(
            modelId=os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620"),
            body=json.dumps({
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.4,
                "anthropic_version": "bedrock-2023-05-31"
            }),
            accept="application/json",
            contentType="application/json"
        )

        raw_body = response["body"].read().decode("utf-8")
        print("📦 Raw Bedrock Output:", raw_body)

        completion = json.loads(raw_body)
        text = completion.get("content", [{}])[0].get("text", "{}")

        try:
            hint_json = json.loads(text)
        except json.JSONDecodeError as je:
            print("⚠️ Failed to parse model output:")
            print(text)
            raise RuntimeError("Model returned malformed JSON.") from je

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Hint retrieved successfully",
                "topic": topic,
                "agent": agent,
                "hint": hint_json.get("hint", "")
            })
        }

    except Exception as e:
        print("❌ Exception while generating hint:")
        traceback.print_exc()
        raise RuntimeError("❌ Error generating lab hint") from e
