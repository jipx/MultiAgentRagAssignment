import os
import boto3
import json
import uuid
from datetime import datetime

# Initialize the SQS client
sqs = boto3.client('sqs')

# Get the SQS queue URL from environment variables
QUEUE_URL = os.environ['QUEUE_URL']

def lambda_handler(event, context):
    try:
        # Parse the JSON body of the request
        body = json.loads(event.get('body') or '{}')
        question = body.get('question')
        user_id = body.get('user_id')
        topic = body.get('topic')

        # Validate required fields
        if not question or not user_id or not topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields: question, user_id, topic'})
            }

        # Create a unique question ID
        question_id = str(uuid.uuid4())

        # Construct the message payload with timestamp
        message = {
            'question_id': question_id,
            'user_id': user_id,
            'question': question,
            'topic': topic,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Send the message to the SQS queue
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        # Return the generated question_id to the client
        return {
            'statusCode': 200,
            'body': json.dumps({'question_id': question_id})
        }

    except Exception as e:
        # Catch and return any unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }