import os
import boto3
import json
import logging
import random
import time
from botocore.exceptions import BotoCoreError, ClientError

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock = boto3.client("bedrock-runtime")
model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID")
region = os.environ.get("AWS_REGION", "ap-northeast-1")

# Construct ARN
account_id = boto3.client("sts").get_caller_identity()["Account"]
kb_arn = f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_id}"

def handle_cloudops_question(question: str) -> str:
    prompt = f"""Human: You are a helpful AWS Cloud Operations assistant.
Use only the knowledge base content to answer the question below.
If the answer is not found, say "I don’t know based on the current knowledge base."

Question: {question}

Assistant:"""

    body = {
        "input": {
            "text": question
        },
        "retrievalConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseArn": kb_arn
        },
        "generationConfiguration": {
            "prompt": prompt,
            "temperature": 0.3,
            "maxTokens": 1024
        }
    }

    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"📡 Invoking Bedrock model: {model_id} for CloudOps KB: {kb_id}")
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps(body),
                contentType="application/json"
            )

            result = json.loads(response["body"].read())
            answer = result.get("outputs", [{}])[0].get("text", "❌ No answer returned.")
            logger.info("✅ Received response from CloudOps KB")
            return answer

        except (BotoCoreError, ClientError, json.JSONDecodeError, KeyError) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"⚠️ Retry {attempt}/{max_retries} failed: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)

    # All retries failed
    logger.error("❌ All attempts failed. Raising error for SQS retry.")
    raise RuntimeError("CloudOps agent failed after multiple retries.")
