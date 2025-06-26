import os
import json
import boto3
from agents.orchestrator import route_question
from utils.dynamodb import save_answer

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Load environment variable for the table
table_name = os.environ['DDB_TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # SQS may batch records; process each message
        for record in event['Records']:
            # Parse message body
            message = json.loads(record['body'])

            question_id = message['question_id']
            user_id = message['user_id']
            question = message['question']
            topic = message['topic']
            timestamp = message.get('timestamp')

            # Route question to appropriate agent and get answer
            answer = route_question(question, topic)

            # Save the answer to DynamoDB
            save_answer(
                table=table,
                question_id=question_id,
                user_id=user_id,
                question=question,
                answer=answer,
                timestamp=timestamp
            )

    except Exception as e:
        # Log the error and re-raise to trigger DLQ or retry
        print(f"Error processing record: {str(e)}")
        raise e