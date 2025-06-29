import os
import boto3
import json
import logging

bedrock = boto3.client("bedrock-runtime")
model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID")
region = os.environ.get("AWS_REGION", "ap-northeast-1")

# Get account ID for ARN construction
account_id = boto3.client("sts").get_caller_identity()["Account"]
kb_arn = f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{kb_id}"

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

    try:
        logger.info(f"📡 Invoking Bedrock model: {model_id} for KB: {kb_id}")
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json"
        )

        result = json.loads(response["body"].read())
        answer = result.get("outputs", [{}])[0].get("text", "❌ No answer returned.")
        return answer

    except Exception as e:
        logger.error(f"❌ Bedrock CloudOps retrieval failed: {e}")
        return "I’m not certain. Please check with your instructor."
