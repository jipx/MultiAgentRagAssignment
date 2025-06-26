# agents/owasp_agent.py

import boto3
import os
import json

# Initialize Bedrock runtime client
bedrock = boto3.client("bedrock-runtime")

# Foundation model ID (adjust if needed for Claude, Titan, etc.)
MODEL_ID = os.environ.get("FM_MODEL_ID", "anthropic.claude-v2")

def handle_owasp_question(question: str) -> str:
    """
    Sends the OWASP-related question to a Foundation Model (FM) via Amazon Bedrock.

    Args:
        question (str): The OWASP-related question.

    Returns:
        str: The generated answer from the FM.
    """
    prompt = f"Answer the following OWASP security-related question in a concise and technical manner:\n\n{question}\n"

    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 300,
                "temperature": 0.5,
                "top_k": 250,
                "top_p": 1,
                "stop_sequences": ["\n
"]
            }),
            contentType="application/json",
            accept="application/json"
        )
        response_body = json.loads(response['body'].read())
        return response_body.get('completion', 'No response generated.')
    except Exception as e:
        return f"Error contacting Foundation Model: {str(e)}"