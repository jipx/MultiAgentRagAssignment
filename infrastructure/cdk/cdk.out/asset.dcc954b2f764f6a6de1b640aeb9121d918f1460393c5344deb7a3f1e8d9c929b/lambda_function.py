import os
import json
import boto3
from agents.orchestrator import route_question
from utils.dynamodb import save_answer

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Load environment variable for the table
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # SQS may batch records; process each message
        for record in event['Records']:
           
              # 🔍 DEBUG: Log the raw message
            print("Raw SQS record body:", record['body'])

            # Parse message body
            message = json.loads(record['body'])

            # 🔍 DEBUG: Log parsed message
            print("Parsed message from SQS:", json.dumps(message, indent=2))


            # Validate input
            required_keys = ['request_id', 'user_id', 'question', 'topic']
            missing = [key for key in required_keys if key not in message]
            if missing:
                raise KeyError(f"Missing required fields in message: {', '.join(missing)}")

            request_id = message['request_id']
            user_id = message['user_id']
            question = message['question']
            topic = message['topic']
            timestamp = message.get('timestamp')

            # Route question to appropriate agent and get answer
            answer = route_question(question, topic)

            # Save the answer to DynamoDB
            save_answer(
                table=table,
                request_id=request_id,
                user_id=user_id,
                question=question,
                answer=answer,
                timestamp=timestamp
            )

    except Exception as e:
        # Log the error and re-raise to trigger DLQ or retry
        print(f"Error processing record: {str(e)}")
        raise e
