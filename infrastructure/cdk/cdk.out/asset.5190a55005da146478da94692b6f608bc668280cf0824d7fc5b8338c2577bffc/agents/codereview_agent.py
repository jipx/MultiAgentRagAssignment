import os
import boto3
import json

def run_codereview_agent(question: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "codereview_prompt.txt")
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()

    model_id = os.environ.get("MODEL_ID", "anthropic.claude-v2")
    use_messages_api = model_id.startswith("anthropic.claude-3")

    if use_messages_api:
        messages = [
            {
                "role": "user",
                "content": template.format(student_code=question)
            }
        ]
        body = json.dumps({
            "messages": messages,
            "max_tokens": 2048
        })
    else:
        raw_prompt = template.format(student_code=question)
        prompt = f"Human:\n{raw_prompt}\n\nAssistant:"
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 2048
        })

    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        accept="application/json",
        contentType="application/json"
    )

    return response["body"].read().decode("utf-8").strip()
