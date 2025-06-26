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
        
         # Try parsing from API Gateway body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct Lambda console/test event
            body = event

       
        question = body.get('question')
        user_id = body.get('user_id')
        topic = body.get('topic')

        # Validate required fields
        if not question or not user_id or not topic:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields: question, user_id, topic'})
            }

        # Create a unique question ID and timestamp
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        # Construct the message payload
        message = {
            'request_id': request_id,
            'user_id': user_id,
            'question': question,
            'topic': topic,
            'timestamp': timestamp
        }

        # Send the message to the SQS queue
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        # Return the full message sent to SQS in the response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': message})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
