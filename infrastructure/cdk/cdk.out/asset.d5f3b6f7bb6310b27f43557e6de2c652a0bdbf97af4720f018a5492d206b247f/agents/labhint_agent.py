import boto3
import os
from jinja2 import Template

def run_labhint_agent(question: str, user_answer: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    with open("prompts/labhint_prompt.txt") as f:
        prompt_template = Template(f.read())

    prompt = prompt_template.render(question=question, user_answer=user_answer)

    response = bedrock.invoke_model(
        modelId=os.environ["BEDROCK_MODEL_ID"],
        body=prompt.encode("utf-8"),
        contentType="text/plain"
    )

    return response["body"].read().decode("utf-8").strip()