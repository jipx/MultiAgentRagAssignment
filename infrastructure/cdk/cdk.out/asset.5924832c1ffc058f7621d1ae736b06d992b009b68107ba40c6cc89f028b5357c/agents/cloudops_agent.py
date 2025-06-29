import os
import boto3
import json
import logging


model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID", os.environ["KB_ID"])  # fallback
region = os.environ.get("AWS_REGION", "ap-northeast-1")


# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock runtime client
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

def handle_cloudops_question(question: str, prompt: str = None) -> str:
    """
    Uses Amazon Bedrock RetrieveAndGenerate to answer cloud operations questions
    with knowledge base context and optional prompt prefix.

    Args:
        question (str): The user's cloudops question.
        prompt (str): An optional prompt prefix to guide the model.

    Returns:
        str: The model-generated answer using KB context.
    """
    logger.info(f"☁️ CloudOps Agent handling question: {question}")

    user_input = f"{prompt.strip()}\n\n{question}" if prompt else question

    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": user_input},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{model_id}"
                }
            }
        )
        return response["output"]["text"]

    except Exception as e:
        logger.error(f"❌ CloudOps Agent Failed to retrieve answer: {e}")
        raise RuntimeError("CloudOps Agent encountered an error.") from e