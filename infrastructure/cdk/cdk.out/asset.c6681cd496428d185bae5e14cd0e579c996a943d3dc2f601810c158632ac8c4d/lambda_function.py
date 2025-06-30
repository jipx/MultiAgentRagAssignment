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