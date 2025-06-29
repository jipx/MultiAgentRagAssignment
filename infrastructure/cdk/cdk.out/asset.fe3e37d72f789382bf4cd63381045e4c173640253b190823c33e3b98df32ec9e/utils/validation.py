import re

def validate_input_fields(body: dict) -> str | None:
    required_fields = ['question', 'user_id', 'topic']
    for field in required_fields:
        if field not in body or not isinstance(body[field], str) or not body[field].strip():
            return f"Invalid or missing field: {field}"

    question = body['question'].strip()
    user_id = body['user_id'].strip()
    topic = body['topic'].strip().lower()

    # ✅ Regex validation for user_id (alphanumeric + underscore, max 15 chars)
    if not re.match(r'^[a-zA-Z0-9_-]{1,15}$', user_id):
        return "Invalid user_id. Only alphanumeric characters and underscores,Hyphen are allowed, and max length is 15."

    # ✅ Regex validation for question (max 100 chars)
    if not re.match(r'^.{1,1000}$', question):
        return "Invalid question. Max length is 1000 characters."

    # ✅ Whitelist validation for topic
    allowed_topics = {"assignment", "owasp", "assignment+owasp","cloudops"}
    if topic not in allowed_topics:
        return f"Invalid topic. Allowed topics are: {', '.join(allowed_topics)}"

    return None
