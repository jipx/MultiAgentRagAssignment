import os
import boto3

def run_codereview_agent(student_code: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "codereview_prompt.txt")
    with open(prompt_path, encoding="utf-8") as f:
        template = f.read()

    prompt = template.format(student_code=student_code)

    response = bedrock.invoke_model(
        modelId=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2"),
        body=prompt.encode("utf-8"),
        contentType="text/plain"
    )

    return response["body"].read().decode("utf-8").strip()
