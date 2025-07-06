import os
import boto3
import json
import uuid
import logging
from datetime import datetime
from utils.validation import validate_input_fields

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

        logger.info(f"Received body: {json.dumps(body)}")

        # ✅ External validation
        validation_error = validate_input_fields(body)
        if validation_error:
            logger.warning(validation_error)
            return {
                'statusCode': 400,
                'body': json.dumps({'error': validation_error})
            }

        question = body['question'].strip()
        user_id = body['user_id'].strip()
        topic = body['topic'].strip().lower()

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

        logger.info(f"Sending message to SQS: {json.dumps(message)}")

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
        logger.error(f"Error in SQS submission Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
