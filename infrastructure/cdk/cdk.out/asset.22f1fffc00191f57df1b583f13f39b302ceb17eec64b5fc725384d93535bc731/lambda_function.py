
import os
import json
import boto3
import logging
from agents.orchestrator import route_question
from utils.dynamodb import save_answer

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    try:
        for record in event['Records']:
            logger.info("Raw SQS record body: %s", record['body'])

            message = json.loads(record['body'])
            logger.info("Parsed message from SQS: %s", json.dumps(message, indent=2))

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
                logger.error("❌ Error from agent (possibly Bedrock): %s", agent_error)
                raise

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
        logger.error("❌ Lambda handler error: %s", str(e))
        raise
