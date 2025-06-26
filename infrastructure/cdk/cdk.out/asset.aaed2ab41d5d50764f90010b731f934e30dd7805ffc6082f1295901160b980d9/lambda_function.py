import os
import boto3
from boto3.dynamodb.conditions import Key
import json

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Reference the DynamoDB table using an environment variable
table = dynamodb.Table(os.environ['DDB_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Extract query parameters from the incoming event
        query_params = event.get('queryStringParameters') or {}
        question_id = query_params.get('question_id')

        # Return a 400 error if question_id is missing
        if not question_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing question_id'})
            }

        # Query the DynamoDB table for the specific question_id
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'QUESTION#{question_id}')
        )

        # Retrieve the items from the query response
        items = response.get('Items', [])

        # If no items found, return a 404 error
        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Answer not found'})
            }

        # Return the answer if found
        return {
            'statusCode': 200,
            'body': json.dumps({'answer': items[0].get('answer', 'No answer yet')})
        }

    except Exception as e:
        # Return a 500 error in case of unexpected exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }