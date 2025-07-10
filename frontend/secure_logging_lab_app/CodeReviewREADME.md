# 🔍 Code Review Tab - OWASP Trainer

This module is a secure coding training interface for reviewing, discussing, and learning from vulnerable OWASP examples using AI feedback and peer collaboration.

## 🚀 Features

| Feature                        | Description                                                                 |
|-------------------------------|-----------------------------------------------------------------------------|
| 🧠 Code Review (via LLM)      | Students submit vulnerable code; feedback is provided by a CodeReview agent |
| 🧵 Threaded Comments          | Users can post and reply to comments; supports threaded discussions         |
| 👍 Voting Support             | Users can upvote comments (limited to once per user per comment)           |
| ☁️ S3-Based Storage           | Code samples and comments are stored in Amazon S3 using presigned URLs      |
| 📥 Dynamic Examples           | OWASP A01–A10 examples are dynamically loaded from S3 in JSON format        |
| 🛠️ Admin Tools                | Admin tab supports bulk comment moderation and dashboard stats              |

## 🧪 OWASP Example Format

```json
[
  {
    "example_id": "a03-xss-bad-regex-001",
    "category": "A03",
    "title": "XSS with Insecure Regex",
    "code": "const input = req.body.name;\nif (!/<script>/i.test(input)) {\n  res.send(input);\n}",
    "validation_pattern": "^[a-zA-Z0-9 .,!?'"]+$"
  }
]
```

## 📂 Comments Format (Threaded)

```json
[
  {
    "comment_id": "uuid",
    "user_id": "student001",
    "parent_id": null,
    "comment": "This regex misses <img> tags.",
    "votes": 3,
    "replies": [
      {
        "comment_id": "uuid2",
        "user_id": "student007",
        "parent_id": "uuid",
        "comment": "Good catch. I'd whitelist instead.",
        "votes": 1
      }
    ]
  }
]
```

## 📦 Folder Structure

- `code_review_tab.py`: Main tab logic
- `README.md`: Documentation
- `owasp_examples_all.zip`: OWASP A01–A10 JSON files