import boto3
import os
import json

# Initialize Bedrock runtime client
bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))

# Foundation model ID for Claude 3.5
MODEL_ID = os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620")

def handle_owasp_question(question: str) -> str:
    """
    Sends the OWASP-related question to Claude 3.5 via Amazon Bedrock Messages API.

    Args:
        question (str): The OWASP-related question.

    Returns:
        str: The generated answer from the Foundation Model.
    """
    try:
        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {"role": "user", "content": question}
                ],
                "max_tokens": 1000,
                "temperature": 0.5
            }),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response['body'].read())
        return result['content'][0]['text']
    except Exception as e:
        return f"Error contacting Foundation Model: {str(e)}"
