import os
import boto3
import json

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Reference the DynamoDB table using an environment variable
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Extract query parameters from the incoming event
        query_params = event.get('queryStringParameters') or {}
        request_id = query_params.get('request_id')

        # Return a 400 error if request_id is missing
        if not request_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing request_id'})
            }

        # Get the item from DynamoDB by request_id (partition key)
        response = table.get_item(Key={'request_id': request_id})
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Answer not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'answer': item.get('answer', 'No answer yet')})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
