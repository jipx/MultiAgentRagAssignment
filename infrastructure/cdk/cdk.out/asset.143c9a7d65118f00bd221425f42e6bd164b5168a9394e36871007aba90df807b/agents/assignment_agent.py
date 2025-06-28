import os
import boto3
import json
import logging
from agents.owasp_agent import handle_owasp_question

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load config
model_id = os.environ["MODEL_ID"]
kb_id = os.environ["KB_ID"]
region = os.environ.get("AWS_REGION", "ap-northeast-1")

# Bedrock runtime client
bedrock_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

# Load prompt template
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "assignment_prompt.txt")
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    static_prompt = f.read().strip()

# Keywords for routing to OWASP expert
OWASP_KEYWORDS = ["injection", "xss", "csrf", "security", "owasp", "sql", "auth", "cookie", "exploit", "vulnerability"]

def is_owasp_related(question: str) -> bool:
    """Simple keyword-based classifier."""
    return any(word in question.lower() for word in OWASP_KEYWORDS)

def expand_if_vague(question: str) -> str:
    """Add clarification to vague inputs."""
    tokens = question.lower().strip().split()
    if len(tokens) <= 4 and not any(char in question for char in "?."):
        return f"can you tell me more about : '{question}'. Can you clarify what the student might be referring to?"
    return question

def handle_assignment_question(question: str) -> str:
    """
    Handles assignment questions. Routes to OWASP agent if security-related.
    Otherwise, queries Bedrock knowledge base.
    """
    logger.info(f"Assignment Agent received question: {question}")

    if is_owasp_related(question):
        logger.info("Detected OWASP-related topic. Routing to OWASP agent.")
        return handle_owasp_question(question)

    expanded_question = expand_if_vague(question)
    full_input = f"{static_prompt}\n\nQuestion: {expanded_question}"

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
