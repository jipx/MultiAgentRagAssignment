import boto3
import os
import json
import logging
from pathlib import Path

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

# Foundation model ID for Claude 3.5
MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620")

# Load prompt template

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "owasp_agent_prompt.txt")

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()

def handle_owasp_question(question: str) -> str:
    """
    Sends the OWASP-related question to Claude 3.5 via Amazon Bedrock Messages API,
    using a structured instructional prompt template.

    Args:
        question (str): The OWASP-related question.

    Returns:
        str: The JSON-formatted answer returned by the model.
    """
    logger.info(f"Handling OWASP question: {question}")

    full_prompt = prompt_template.replace("{question}", question)

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.4
        }),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response['body'].read())
    logger.info("Received response from Claude 3.5")
    return result['content'][0]['text']
