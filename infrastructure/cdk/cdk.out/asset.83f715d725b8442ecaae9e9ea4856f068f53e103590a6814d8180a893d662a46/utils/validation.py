import re

def validate_input_fields(body: dict) -> str | None:
    required_fields = ['question', 'user_id', 'topic']
    for field in required_fields:
        if field not in body or not isinstance(body[field], str) or not body[field].strip():
            return f"Invalid or missing field: {field}"

    question = body['question'].strip()
    user_id = body['user_id'].strip()
    topic = body['topic'].strip().lower()

    # ✅ Regex validation for user_id (alphanumeric + underscore, max 10 chars)
    if not re.match(r'^[a-zA-Z0-9_]{1,10}$', user_id):
        return "Invalid user_id. Only alphanumeric characters and underscores are allowed, and max length is 10."

    # ✅ Regex validation for question (max 100 chars)
    if not re.match(r'^.{1,100}$', question):
        return "Invalid question. Max length is 100 characters."

    # ✅ Whitelist validation for topic
    allowed_topics = {"assignment", "owasp", "assignment+owasp"}
    if topic not in allowed_topics:
        return f"Invalid topic. Allowed topics are: {', '.join(allowed_topics)}"

    return None
