import boto3
import os
import json
import logging
import random

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

# Foundation model ID for Claude 3.5 (Sonnet)
MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620")

# Load prompt template
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "owasp_agent_prompt.txt")

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()

def get_random_difficulty(weighted=True):
    """Generate a random difficulty level (1-5)."""
    if weighted:
        return random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.3, 0.25, 0.2, 0.15, 0.1],
            k=1
        )[0]
    return random.randint(1, 5)

def handle_owasp_question(question: str, difficulty: int = None) -> str:
    """
    Sends the OWASP-related question to Claude 3.5 via Amazon Bedrock Messages API,
    using a structured instructional prompt template.

    Args:
        question (str): The OWASP-related question.
        difficulty (int, optional): Difficulty level (1-5). Randomized if not provided.

    Returns:
        str: The JSON-formatted answer returned by the model.
    """
    logger.info(f"Handling OWASP question: {question}")

    difficulty_level = difficulty or get_random_difficulty()
    logger.info(f"Using difficulty level: {difficulty_level}")

    full_prompt = prompt_template \
        .replace("{question}", question) \
        .replace("{difficulty_level}", str(difficulty_level))

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
