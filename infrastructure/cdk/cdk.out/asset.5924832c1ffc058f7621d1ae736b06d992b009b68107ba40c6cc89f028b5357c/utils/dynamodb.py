def save_answer(table, request_id, user_id, question, answer, timestamp=None):
    """
    Saves the answer and metadata to DynamoDB.

    Args:
        table (boto3 DynamoDB.Table): The table to write to.
        request_id (str): Unique ID of the question/request.
        user_id (str): ID of the user who asked the question.
        question (str): The user's question.
        answer (str): The answer returned by the model.
        timestamp (str, optional): Timestamp of the request.
    """
    item = {
        "request_id": request_id,
        "user_id": user_id,
        "question": question,
        "answer": answer
    }

    if timestamp:
        item["timestamp"] = timestamp

    table.put_item(Item=item)
