import json
import boto3
import os
import traceback
import re  # Needed for regex-based JSON extraction

bedrock = boto3.client("bedrock-runtime")

# Few-shot examples to guide the model's behavior
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
        # Construct the prompt as a single user message
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

        # Invoke Bedrock model with Anthropic Claude 3.5
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

        # Read the raw model response as a string
        raw_body = response["body"].read().decode("utf-8")
        print("📦 Raw Bedrock Output:", raw_body)

        # Parse top-level JSON returned by Bedrock
        completion = json.loads(raw_body)

        # Extract the content of the assistant's message
        # This usually includes natural language + structured data
        text = completion.get("content", [{}])[0].get("text", "{}")

        # Extract the JSON block embedded inside the text (skip intro)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            # Fail gracefully if no JSON object is detected
            raise RuntimeError("❌ No JSON object found in model response.")
        
        json_str = match.group()

        try:
            # Attempt to parse the extracted JSON string
            hint_json = json.loads(json_str)
        except json.JSONDecodeError as je:
            # Print raw text for debugging before raising the error
            print("⚠️ Failed to parse model output:")
            print(text)
            raise RuntimeError("Model returned malformed JSON.") from je

        # Return the parsed hint with topic/agent metadata
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": {
                    "answer": hint_json,  # ✅ Safe parsed dict
                    "topic": topic,
                    "agent": agent
                }
            })
        }

    except Exception as e:
        # Catch-all exception block with stack trace
        print("❌ Exception while generating hint:")
        traceback.print_exc()
        raise RuntimeError("❌ Error generating lab hint") from e
