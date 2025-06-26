
## 🔐 API Throttling Test via Postman

You can test throttling settings in your API Gateway by sending rapid requests using Postman.

### Steps:

1. Open Postman and create a request to:
   ```http
   POST https://<api_id>.execute-api.<region>.amazonaws.com/prod/ask
   ```

2. Use the following JSON body with dynamic request_id:
   ```json
   {
     "request_id": "test-{{$timestamp}}",
     "user_id": "loadtest-user",
     "question": "What is XSS?",
     "topic": "owasp",
     "timestamp": "{{$isoTimestamp}}"
   }
   ```

3. Go to **Runner**, select number of iterations (e.g., 100), set delay (optional), and run.

4. Monitor API Gateway metrics and CloudWatch logs for throttling events.


## 🚀 Load Simulation Using Python

You can simulate load against the POST `/ask` endpoint to test the performance of SQS and Lambda.

Sample Payload sent to API Gateway
```
{
  "request_id": "test-1234",
  "user_id": "student-001",
  "question": "What is SQL injection?",
  "topic": "owasp",
  "timestamp": "2025-10-01T12:00:00Z"
}

```

### Python Script

```python
import requests, threading, uuid
from datetime import datetime

API_URL = "https://<api_id>.execute-api.<region>.amazonaws.com/prod/ask"

def send_request():
    payload = {
        "request_id": str(uuid.uuid4()),
        "user_id": "loaduser",
        "question": "How does SQL injection work?",
        "topic": "owasp",
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        r = requests.post(API_URL, json=payload)
        print(r.status_code, r.text)
    except Exception as e:
        print("Error:", e)

# Launch 50 concurrent requests
threads = [threading.Thread(target=send_request) for _ in range(50)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### What to Monitor in AWS

| Metric                               | AWS Service    |
|--------------------------------------|----------------|
| `ApproximateNumberOfMessagesVisible` | SQS            |
| `ConcurrentExecutions`              | Lambda Worker  |
| `5XXError`                          | API Gateway    |
| `Throttles`                         | Lambda/API GW  |
| CloudWatch Logs                     | All services   |


## 📊 Visualizing Load Test Metrics in CloudWatch

After performing API throttling and load tests, use **Amazon CloudWatch** to monitor key metrics.

### 🔎 Dashboards and Metrics

| Metric Name                                  | Service         | Description                                         |
|----------------------------------------------|------------------|-----------------------------------------------------|
| `ApproximateNumberOfMessagesVisible`         | Amazon SQS       | Pending messages not yet processed by Lambda        |
| `NumberOfMessagesDeleted`                    | Amazon SQS       | Messages successfully processed and removed         |
| `Throttles`                                  | AWS Lambda/API GW| Number of throttled requests                        |
| `5XXError`                                   | API Gateway      | Indicates failures on API backends                  |
| `ConcurrentExecutions`                       | AWS Lambda       | Number of Lambda executions running in parallel     |
| `Duration`, `Invocations`, `Errors`          | AWS Lambda       | Track performance and failures                      |

### 📈 Steps to Create CloudWatch Dashboard

1. Open the **CloudWatch Console** → Dashboards → **Create dashboard**
2. Choose `Line` or `Stacked Area` graphs
3. Add widgets for:
   - SQS > `ApproximateNumberOfMessagesVisible`
   - Lambda > `Invocations`, `Errors`, `Throttles`, `Duration`
   - API Gateway > `5XXError`, `Latency`, `IntegrationLatency`

### 🧠 Tips

- Set filters per function/API or SQS queue name
- Use a 1-minute granularity for short tests
- Enable **CloudWatch Alarms** for auto-notification (e.g., DLQ has > 0 messages)


## 🚨 Setting Up CloudWatch Alarms

To proactively monitor issues during load testing or production, configure **CloudWatch Alarms** for key thresholds.

### 🔔 Example Alarms to Set

| Alarm Name             | Metric                             | Condition                             | Action                        |
|------------------------|-------------------------------------|----------------------------------------|-------------------------------|
| `DLQ Alarm`            | `ApproximateNumberOfMessagesVisible` (DLQ) | >= 1 message                          | Notify via SNS/email          |
| `Lambda Error Alarm`   | `Errors` (Lambda Worker)            | > 0 errors in 5 minutes                | Notify via SNS/email          |
| `Throttling Alarm`     | `Throttles` (Lambda or API Gateway) | > 0 throttles                          | Review throttling limits      |
| `Latency Alarm`        | `Latency` (API Gateway)             | > 1000 ms average latency              | Optimize endpoint performance |

### 🧰 How to Create an Alarm

1. Open **CloudWatch Console** → Alarms → **Create alarm**
2. Select the metric (e.g., Lambda > Worker > `Errors`)
3. Define threshold (e.g., `Greater than 0`)
4. Choose **1 out of 1 evaluation period** (for quick feedback)
5. Set up an **SNS topic** for notifications
6. Add email/phone recipients for alerting

### 🧪 Testing Alarm

- You can simulate a failing Lambda (e.g., throw an error) and monitor if alarm is triggered.
- Trigger an API throttling by sending >10 RPS (default burst) and check alarm logs.

