import boto3
import os
from jinja2 import Template

def run_codereview_agent(code: str, lab_notes: str, owasp_top10: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    with open("prompts/codereview_prompt.txt") as f:
        template = Template(f.read())

    prompt = template.render(code=code, lab_notes=lab_notes, owasp_top10=owasp_top10)

    response = bedrock.invoke_model(
        modelId=os.environ["BEDROCK_MODEL_ID"],
        body=prompt.encode("utf-8"),
        contentType="text/plain"
    )

    return response["body"].read().decode("utf-8").strip()