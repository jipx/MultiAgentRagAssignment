import re

def validate_input_fields(body: dict) -> str | None:
    required_fields = ['question', 'user_id', 'topic']
    for field in required_fields:
        if field not in body or not isinstance(body[field], str) or not body[field].strip():
            return f"Invalid or missing field: {field}"

    question = body['question'].strip()
    user_id = body['user_id'].strip()
    topic = body['topic'].strip().lower()

    # ✅ Regex validation for user_id (alphanumeric + underscore and hyphen, max 15 chars)
    if not re.match(r'^[a-zA-Z0-9_-]{1,15}$', user_id):
        return "Invalid user_id. Only alphanumeric characters, underscores, and hyphens are allowed, with a max length of 15."

    # ✅ Length validation for question
    if not (1 <= len(question) <= 10000):
        return "Invalid question. Max length is 10000 characters."

    # ✅ Whitelist validation for topic
    allowed_topics = {"assignment", "owasp", "assignment+owasp", "cloudops", "sc-labquiz-gen"}
    if topic not in allowed_topics:
        return f"Invalid topic. Allowed topics are: {', '.join(sorted(allowed_topics))}"

    return None
