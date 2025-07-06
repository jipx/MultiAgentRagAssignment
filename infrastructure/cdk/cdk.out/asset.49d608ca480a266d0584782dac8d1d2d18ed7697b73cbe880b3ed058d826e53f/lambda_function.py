import os
import boto3
import json
from decimal import Decimal

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

# Helper function to convert Decimal types to int or float
def clean_decimal(obj):
    if isinstance(obj, list):
        return [clean_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: clean_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    else:
        return obj

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        request_id = query_params.get('request_id')

        if not request_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing request_id'})
            }

        response = table.get_item(Key={'request_id': request_id})
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Answer not found'})
            }

        # Sanitize Decimal types before returning
        clean_item = clean_decimal(item)

        return {
            'statusCode': 200,
            'body': json.dumps({'answer': clean_item.get('answer', 'No answer yet')})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
