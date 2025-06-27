# agents/assignment_agent.py

import os
import boto3
import json
import logging
from pathlib import Path
from agents.owasp_agent import handle_owasp_question  # Import fallback

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

model_id = os.environ["MODEL_ID"]
kb_id = os.environ["KB_ID"]
region = os.environ.get("AWS_REGION", "ap-northeast-1")

bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

# Load the static assignment prompt in the prompts folder
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "assignment_prompt.txt")

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    static_prompt = f.read().strip()



def handle_assignment_question(question: str) -> str:
    """
    Answers assignment-related questions. If the topic overlaps with OWASP,
    it defers to the OWASP agent.
    """
    logger.info(f"Assignment Agent received question: {question}")

   
    full_input = f"{static_prompt}\n\nQuestion: {question}"
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
