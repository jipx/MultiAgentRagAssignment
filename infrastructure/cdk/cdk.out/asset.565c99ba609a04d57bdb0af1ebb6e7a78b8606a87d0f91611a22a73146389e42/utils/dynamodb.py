# utils/dynamodb.py

import time

def save_answer(table, question_id, user_id, question, answer, timestamp=None):
    """
    Saves the question and answer record to DynamoDB.

    Args:
        table: The DynamoDB Table resource.
        question_id (str): Unique ID for the question.
        user_id (str): ID of the user who asked the question.
        question (str): The question text.
        answer (str): The answer text.
        timestamp (str): Optional ISO timestamp; if not provided, uses current time.
    """
    if not timestamp:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    item = {
        'PK': f'USER#{user_id}',           # Partition key to group by user
        'SK': f'QUESTION#{question_id}',   # Sort key to order by question
        'question_id': question_id,
        'user_id': user_id,
        'question': question,
        'answer': answer,
        'timestamp': timestamp
    }

    table.put_item(Item=item)