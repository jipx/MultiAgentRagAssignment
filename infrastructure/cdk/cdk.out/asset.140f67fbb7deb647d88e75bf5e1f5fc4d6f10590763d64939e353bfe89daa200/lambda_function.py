import boto3
import json
import os
from datetime import datetime

s3 = boto3.client('s3')
SOURCE_BUCKET = os.environ['SOURCE_BUCKET']

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        filename = body.get('filename')
        action = body.get('action', 'get')  # 'get', 'put', or 'delete'

        if not filename:
            raise ValueError("Filename is required")

        key = filename if '/' in filename else f"samples/{filename}"

        params = {'Bucket': SOURCE_BUCKET, 'Key': key}
        if action == 'put':
            params['ContentType'] = 'application/json'

        signed_url = s3.generate_presigned_url(
            ClientMethod=f'{action}_object',
            Params=params,
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"url": signed_url, "s3_key": key}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }
