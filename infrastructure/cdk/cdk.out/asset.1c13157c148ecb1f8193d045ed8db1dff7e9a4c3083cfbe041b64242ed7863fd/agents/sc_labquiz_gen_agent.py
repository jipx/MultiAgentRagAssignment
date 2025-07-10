import json
import boto3
import os
import traceback
import re
import ast

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
        # Prompt with explicit JSON format and strict structure
        prompt = f"""You are a secure coding lab assistant.

Generate exactly 10 multiple-choice questions in **valid JSON format** based on the provided lab notes.

Each question must follow this structure:

{{
  "question": "What is ...?",
  "choices": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Option A",
  "explanation": "Explanation of why this answer is correct."
}}

Return the final result as a JSON object:

{{
  "questions": [
    // 10 questions like above
  ]
}}

Only return the valid JSON. Do **not** include markdown formatting, explanations, comments, or extra text.

Here are a few-shot examples:
{FEW_SHOT_EXAMPLES}

Lab notes:
\"\"\"{question}\"\"\"
"""

        # Claude 3 Messages API call
        response = bedrock.invoke_model(
            modelId=os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620"),
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.3
            }),
            accept="application/json",
            contentType="application/json"
        )

        # Parse the Claude response body
        raw_body = response["body"].read().decode("utf-8")
        print("📦 Raw Bedrock Output:", raw_body)

        completion_text = json.loads(raw_body).get("content", [{}])[0].get("text", "{}")

        # Auto-remove markdown code block if present (e.g., ```json\n{...}\n```)
        if completion_text.startswith("```"):
            completion_text = re.sub(r"^```(?:json)?\s*", "", completion_text)
            completion_text = re.sub(r"\s*```$", "", completion_text)

        # Try to extract top-level JSON block
        match = re.search(r'\{[\s\S]*\}', completion_text)
        if not match:
            raise RuntimeError("❌ No JSON object found in model response.")

        json_str = match.group()

        # Normalize smart quotes
        json_str = json_str.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

        # Parse JSON safely
        try:
            questions_json = json.loads(json_str)
        except json.JSONDecodeError:
            print("⚠️ JSON parsing failed. Trying ast.literal_eval as fallback...")
            try:
                repaired = ast.literal_eval(json_str)
                questions_json = json.loads(json.dumps(repaired))  # Normalize to proper JSON
            except Exception as fallback_error:
                print("❌ Fallback also failed. Final raw response:")
                print(completion_text)
                raise RuntimeError("Model returned malformed JSON.")

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
