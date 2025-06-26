import os
import json
import boto3
from agents.orchestrator import route_question
from utils.dynamodb import save_answer

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            # 🔍 Log raw message for debugging
            print("Raw SQS record body:", record['body'])

            message = json.loads(record['body'])
            print("Parsed message from SQS:", json.dumps(message, indent=2))

            # ✅ Ensure required fields are present
            required_keys = ['request_id', 'user_id', 'question', 'topic']
            missing = [key for key in required_keys if key not in message]
            if missing:
                raise KeyError(f"Missing required fields in message: {', '.join(missing)}")

            request_id = message['request_id']
            user_id = message['user_id']
            question = message['question']
            topic = message['topic']
            timestamp = message.get('timestamp')

            # 🧠 Call the appropriate agent
            try:
                answer = route_question(question, topic)
            except Exception as agent_error:
                print(f"❌ Error from agent (possibly Bedrock): {agent_error}")
                raise  # ⬅️ Re-raise to ensure message is retried

            # 💾 Save result to DynamoDB
            save_answer(
                table=table,
                request_id=request_id,
                user_id=user_id,
                question=question,
                answer=answer,
                timestamp=timestamp
            )

    except Exception as e:
        print(f"❌ Lambda handler error: {str(e)}")
        raise  # ⬅️ Critical: re-raise so SQS makes the message visible again
