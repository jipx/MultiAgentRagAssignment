import os
import boto3
import json
import logging

bedrock = boto3.client("bedrock-runtime")
model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID", os.environ["KB_ID"])  # fallback
region = os.environ.get("AWS_REGION", "ap-northeast-1")


# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_cloudops_question(question: str) -> str:
    prompt = f"""Human: Use the knowledge base to answer the question below as clearly and completely as possible.
Question: {question}
Assistant:"""

    
    try:
        response = bedrock_runtime.retrieve_and_generate(
            input={"text": full_input},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb_id,
                    "modelArn": f"arn:aws:bedrock:{region}::foundation-model/{model_id}"
                }
            }
        )
        logger.info("Received response from Bedrock Assignment KB")
        return response["output"]["text"]

    except Exception as e:
        logger.error(f"❌ Failed to retrieve answer: {e}")
        return "I’m not certain. Please check with your instructor."