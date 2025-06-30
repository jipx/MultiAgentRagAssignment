# 📄 Presigned URL API Integration Guide for RAG CDK Backend

This guide explains how to add a `/presigned-url` API endpoint to your existing AWS CDK backend project to support secure S3 uploads and downloads for Bedrock Knowledge Base ingestion.

---

## ✅ Purpose

Enable the client (e.g., Streamlit app) to:
- 🔼 Upload JSON chunks to S3 securely (PUT)
- 🔽 Download processed files securely (GET)

---

## 📁 Files to Add

### `lambda/lambda_presigned_url.py`
```python
import json
import boto3
import os

s3 = boto3.client("s3")
bucket_name = os.environ["BUCKET_NAME"]

def handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        key = body["key"]
        method = body.get("method", "get")

        if method not in ("get", "put"):
            return {"statusCode": 400, "body": "Invalid method"}

        url = s3.generate_presigned_url(
            ClientMethod="put_object" if method == "put" else "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"url": url})
        }
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
```

---

## 🏗️ CDK Integration (inside your existing stack)

### Step 1: Imports
```python
from aws_cdk import aws_lambda as _lambda, aws_apigateway as apigw, aws_s3 as s3
```

### Step 2: Add to Your Stack Class
```python
bucket_name = self.node.try_get_context("kb_bucket_name")
bucket = s3.Bucket.from_bucket_name(self, "KnowledgeBaseBucket", bucket_name)

presign_lambda = _lambda.Function(
    self, "PresignedURLFunction",
    runtime=_lambda.Runtime.PYTHON_3_11,
    handler="lambda_presigned_url.handler",
    code=_lambda.Code.from_asset("lambda"),
    environment={"BUCKET_NAME": bucket.bucket_name}
)

bucket.grant_read_write(presign_lambda)

api = getattr(self, "api", apigw.RestApi(self, "RagAPI", rest_api_name="RAG API"))

api.root.add_resource("presigned-url").add_method(
    "POST",
    apigw.LambdaIntegration(presign_lambda)
)
```

### Step 3: Context in `cdk.json`
```json
{
  "context": {
    "kb_bucket_name": "your-kb-bucket-name"
  }
}
```

---

## 🚀 Deploy
```bash
cdk deploy -c kb_bucket_name=your-kb-bucket-name
```

---

## 🔍 Testing the Presigned URL API

### ✅ 1. Using `curl`
```bash
curl -X POST https://<your-api>.execute-api.<region>.amazonaws.com/prod/presigned-url \
  -H "Content-Type: application/json" \
  -d '{"key": "test/upload.json", "method": "put"}'
```

### 🔼 Upload File to S3
```bash
curl -X PUT --upload-file path/to/file.json "<presigned PUT url>"
```

### 🔽 Download from S3
```bash
curl -X POST https://<your-api>.execute-api.<region>.amazonaws.com/prod/presigned-url \
  -H "Content-Type: application/json" \
  -d '{"key": "test/upload.json", "method": "get"}'
```

Use the returned URL in your browser or:
```bash
curl -o downloaded.json "<presigned GET url>"
```

---

## 🧪 Python Test Script
```python
import requests

# Generate presigned PUT URL
res = requests.post("https://your-api/presigned-url", json={"key": "test/file.json", "method": "put"})
upload_url = res.json()["url"]

# Upload a file
with open("file.json", "rb") as f:
    put_res = requests.put(upload_url, data=f)

print("Upload status:", put_res.status_code)
```

---

For questions or automation scripts, contact your RAG backend maintainer.
