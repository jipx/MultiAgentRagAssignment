import os
import json
import logging
import time
import random
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment config
model_id = os.environ["MODEL_ID"]
kb_id = os.environ["CLOUDOPS_KB_ID"]
region = os.environ.get("AWS_REGION", "ap-northeast-1")

# Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name=region)

# Construct ARN
account_id = boto3.client("sts").get_caller_identity()["Account"]
kb_arn = f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_id}"

# Load structured prompt
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "cloudops_agent_prompt.txt")
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    static_prompt = f.read()

def handle_cloudops_question(question: str, max_retries: int = 3) -> str:
    """
    Sends a CloudOps-related question to Bedrock knowledge base using a structured prompt,
    with exponential retry for transient failures.

    Args:
        question (str): User question
        max_retries (int): Retry attempts on transient failure

    Returns:
        str: Answer from the model or fallback message
    """
    prompt = static_prompt.replace("{question}", question)

    body = {
        "input": {"text": question},
        "retrievalConfiguration": {"type": "KNOWLEDGE_BASE", "knowledgeBaseArn": kb_arn},
        "generationConfiguration": {
            "prompt": prompt,
            "temperature": 0.3,
            "maxTokens": 1024
        }
    }

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"📡 Calling Bedrock model (Attempt {attempt})")
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            result = json.loads(response["body"].read())
            answer = result.get("outputs", [{}])[0].get("text", "❌ No answer returned.")
            logger.info("✅ Successfully retrieved CloudOps answer")
            return answer

        except (BotoCoreError, ClientError, json.JSONDecodeError, KeyError) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"[CLOUDOPS] Attempt {attempt} failed: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)


    # All retries failed – raise exception to trigger SQS redelivery
    logger.error("[CLOUDOPS] All retry attempts failed. Raising exception for SQS redelivery.")
    raise RuntimeError("Failed to get a response from Bedrock after multiple retries.")

