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

def run_labhint_agent(task: str, topic: str = "Secure Coding Lab", agent: str = "labhints") -> dict:
    try:
        prompt = f"""Human: You are a helpful assistant for secure coding lab students.
Your job is to give clear, concise **hints** (not solutions) to help them complete lab tasks.

{FEW_SHOT_HINTS}

Now provide a helpful hint for this lab task:
\"\"\"{task}\"\"\"

Return format:
{{
  "hint": "..."
}}
Assistant:"""

        response = bedrock.invoke_model(
            modelId=os.environ.get("MODEL_ID", "anthropic.claude-v2"),
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 512
            }),
            accept="application/json",
            contentType="application/json"
        )

        raw_body = response["body"].read().decode("utf-8")
        print("📦 Raw Bedrock Output:", raw_body)

        completion_text = json.loads(raw_body).get("completion", "{}")

        try:
            hint_json = json.loads(completion_text)
        except json.JSONDecodeError as je:
            print("⚠️ Failed to parse model output:")
            print(completion_text)
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
