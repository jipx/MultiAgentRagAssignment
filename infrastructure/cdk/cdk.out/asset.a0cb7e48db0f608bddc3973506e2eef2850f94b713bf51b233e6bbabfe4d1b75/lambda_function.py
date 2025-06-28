import os
import json
import boto3
from boto3.dynamodb.conditions import Attr

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('user_id')

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing user_id'})
            }

        # Scan table and filter by user_id (not efficient at scale)
        response = table.scan(
            FilterExpression=Attr('user_id').eq(user_id)
        )

        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'No history found for user_id {user_id}'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps({'history':  items}),
            'headers':{
                'Content-Type': 'application/json'
             }
        }
   
  
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
