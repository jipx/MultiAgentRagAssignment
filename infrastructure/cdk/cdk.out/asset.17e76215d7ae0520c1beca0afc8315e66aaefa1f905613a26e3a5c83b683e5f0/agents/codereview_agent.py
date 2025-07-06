import os
import boto3
import json

def run_codereview_agent(question: str) -> str:
    bedrock = boto3.client("bedrock-runtime")

    model_id = os.environ.get("MODEL_ID", "anthropic.claude-3-5-sonnet-20240620")

    # Use Claude 3 Messages API format
    prompt = """You are a secure coding reviewer.

Use your knowledge of secure coding practices and the OWASP Top 10 to review the student's code. Focus on identifying security flaws, anti-patterns, and missing safeguards.

Specifically consider:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

Student Code:
{student_code}

Give your review:
- What the code does (summary)
- Potential vulnerabilities
- Recommendations for improvement
"""

    student_code = question.strip() if question else "[Code not provided]"
    prompt_text = prompt.format(student_code=student_code)

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",  # required for Claude 3
        "messages": [
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        "max_tokens": 2048
    })

    response = bedrock.invoke_model(
        modelId=model_id,
        body=body,
        accept="application/json",
        contentType="application/json"
    )

    return response["body"].read().decode("utf-8").strip()
