import os
import boto3
import json

bedrock = boto3.client("bedrock-runtime")
model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID", os.environ["KB_ID"])  # fallback

def handle_cloudops_question(question: str) -> str:
    prompt = f"""Human: Use the knowledge base to answer the question below as clearly and completely as possible.
Question: {question}
Assistant:"""

    body = {
        "input": {
            "text": question
        },
        "retrievalConfiguration": {
            "knowledgeBaseArn": f"arn:aws:bedrock:{os.environ['AWS_REGION']}:{os.environ['AWS_ACCOUNT_ID']}:knowledge-base/{kb_id}",
            "type": "KNOWLEDGE_BASE"
        },
        "generationConfiguration": {
            "prompt": prompt,
            "temperature": 0.7,
            "maxTokens": 1024
        }
    }

    response = bedrock.invoke_model(
        body=json.dumps(body),
        contentType="application/json",
        modelId=model_id
    )

    result = json.loads(response['body'].read().decode())
    return result.get("outputs", [{}])[0].get("text", "❌ No response generated.")
