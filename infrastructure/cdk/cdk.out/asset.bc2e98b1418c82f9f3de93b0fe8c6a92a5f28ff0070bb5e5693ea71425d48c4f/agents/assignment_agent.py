# agents/assignment_agent.py

import os
import boto3
import json

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
    try:
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
        return response["output"]["text"]

    except Exception as e:
        return f"Sorry, there was an error retrieving the answer: {str(e)}"
