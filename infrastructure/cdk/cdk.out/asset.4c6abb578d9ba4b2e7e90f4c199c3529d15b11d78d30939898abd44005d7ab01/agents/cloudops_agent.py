import os
import boto3

bedrock = boto3.client("bedrock-runtime")
model_id = os.environ["MODEL_ID"]
kb_id = os.environ.get("CLOUDOPS_KB_ID", os.environ["KB_ID"])  # fallback

def handle_cloudops_question(question: str) -> str:
    response = bedrock.retrieve_and_generate(
        input={
            "input": {
                "text": question
            },
            "knowledgeBaseId": kb_id
        },
        modelId=model_id
    )
    return response["output"]["text"]
