# agents/assignment_agent.py


import os
import boto3
import json
import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

model_id = os.environ["MODEL_ID"]
kb_id = os.environ["KB_ID"]
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

def handle_assignment_question(question: str) -> str:
    """
    Uses Amazon Bedrock's RetrieveAndGenerate API to answer assignment-related questions
    with context from the linked knowledge base.

    Args:
        question (str): The user's question.

    Returns:
        str: The model-generated answer using KB context.
    """
    logger.info(f"Handling assignment question: {question}")
    response = bedrock_runtime.retrieve_and_generate(
        input={
            "text": question
        },
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": kb_id,
                "modelArn": f"arn:aws:bedrock:{bedrock_runtime.meta.region_name}::foundation-model/{model_id}"
            }
        }
    )
    logger.info("Received response from Bedrock")
    return response["output"]["text"]
