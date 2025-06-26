import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Reference the DynamoDB table using an environment variable
table = dynamodb.Table(os.environ['DDB_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        # Extract query parameters from the event
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('user_id')

        # Return a 400 error if user_id is missing
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing user_id'})
            }

        # Query all items associated with the user
        # Assumes the primary key (PK) is in the format 'USER#{user_id}'
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}')
        )

        # Retrieve the list of items from the query result
        items = response.get('Items', [])

        # Format each item into a Q&A pair with question ID
        history = [
            {
                'question_id': item.get('SK', ''),
                'question': item.get('question', ''),
                'answer': item.get('answer', '')
            }
            for item in items
        ]

        # Return the formatted history list
        return {
            'statusCode': 200,
            'body': json.dumps({'history': history})
        }

    except Exception as e:
        # Catch and return any unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }