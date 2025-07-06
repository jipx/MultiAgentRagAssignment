import boto3
import os

def run_labhint_agent(question: str, user_answer: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    # Load template from file using .format placeholders
    with open("prompts/labhint_prompt.txt", encoding="utf-8") as f:
        template = f.read()

    # Fill in placeholders using .format
    prompt = template.format(question=question, user_answer=user_answer)

    response = bedrock.invoke_model(
        modelId=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2"),
        body=prompt.encode("utf-8"),
        contentType="text/plain"
    )

    return response["body"].read().decode("utf-8").strip()
