import boto3
import os
import json
import logging
import random
import time
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620")

PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "owasp_agent_prompt.txt")
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()

def get_random_difficulty(weighted=True):
    return random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.25, 0.2, 0.15, 0.1], k=1)[0] if weighted else random.randint(1, 5)

def handle_owasp_question(question: str, difficulty: int = None) -> str:
    logger.info(f"[OWASP] Handling question: {question}")
    difficulty_level = difficulty or get_random_difficulty()
    logger.info(f"[OWASP] Using difficulty level: {difficulty_level}")

    full_prompt = prompt_template.replace("{question}", question).replace("{difficulty_level}", str(difficulty_level))

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": 1500,
        "temperature": 0.4
    }

    max_retries = 1
    for attempt in range(1, max_retries + 1):
        try:
            response = bedrock.invoke_model(
                modelId=MODEL_ID,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response['body'].read())
            logger.info("[OWASP] Successfully received response.")
            return result['content'][0]['text']
        except (BotoCoreError, ClientError, json.JSONDecodeError, KeyError) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"[OWASP] Attempt {attempt} failed: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    # All retries failed – raise exception to trigger SQS redelivery
    logger.error("[OWASP] All retry attempts failed. Raising exception for SQS redelivery.")
    raise RuntimeError("Failed to get a response from Bedrock after multiple retries.")
