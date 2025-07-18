# 🧠 Lab-Based Adaptive Learning Report

## Executive Summary

This report outlines the architecture and pedagogical design of a lab-based adaptive learning system developed for secure coding education, specifically Practical 5 on secure logging. The system leverages generative AI to dynamically produce formative assessments in the form of quizzes based on lab notes. Integration with Streamlit, AWS Lambda, Amazon SQS, and Bedrock Claude facilitates an automated pipeline that enhances individualized learning and knowledge reinforcement.

---

## System Architecture

### 📄 Quiz Generation Flow (`POST /ask` → `SQS` → `sc-labquiz-gen`)
![Description](images/diagram-export-7-4-2025-9_03_46-AM.png)
https://app.eraser.io/workspace/EGa4u8QN1AtBzCPDdjF6?origin=share

```
[ 👩‍🎓 User (Streamlit App) ]
   |
   | Enters lab topic and clicks "Generate Quiz"
   
[ API Gateway: POST /ask ]
   |
   | Payload:
   | {
   |   "topic": "Practical 5",
   |   "agent": "sc-labquiz-gen",
   |   "question": "<full lab notes markdown content>"
   | }
   v
[ Amazon SQS: SecureCodingRAGQueue ]
   |
   v
[ Worker Lambda Function ]
   ├─ Recognizes agent = "sc-labquiz-gen"
   ├─ Sends prompt to Bedrock Claude
   ├─ Receives quiz in JSON/Markdown format
   └─ Saves response to DynamoDB:
       • topic
       • agent
       • question
       • response
       • timestamp
```

> **Note**: The lab content uploaded by the user is used as the input payload (`question` field) to generate the quiz, ensuring that the output is contextually tailored to specific lab instructions and concepts.

### 🔕 Quiz Retrieval Flow (`GET /get-answer`)

```
[ 👩‍🎓 User (Streamlit App) ]
   |
   | Clicks "Load Quiz"
   v
[ API Gateway: GET /get-answer ]
   | Query: ?topic=Practical%205&agent=sc-labquiz-gen
   v
[ get-answer Lambda ]
   ├─ Queries DynamoDB with topic & agent
   └─ Returns:
       {
         "topic": "Practical 5",
         "agent": "sc-labquiz-gen",
         "response": "<quiz markdown>"
       }
   v
[ Streamlit ]
   └─ Renders the quiz for user interaction
```

[![Watch the 3 miniute video on YouTube](https://img.youtube.com/vi/D92BFXhyBKc/0.jpg)](https://www.youtube.com/watch?v=D92BFXhyBKc/0.jpg)
---

## Pedagogical Foundations

### Constructivist Learning

The system encourages active learning by prompting students to interact with lab-based content through quiz challenges, fostering meaningful knowledge construction aligned with constructivist principles.

### Formative Assessment

By generating quizzes directly tied to lab activities, the system supports continuous formative assessment. Learners receive immediate feedback, reinforcing key concepts and allowing instructors to identify misconceptions early.

### Adaptive Learning Design

Quiz generation is personalized to the specific lab content and sub-topic selected by the user. This allows differentiated instruction, tailored to individual learning progress and lab context.

### Cognitive Load Reduction

The integration of automated quiz creation reduces extraneous cognitive load on instructors and allows learners to focus on key cognitive tasks like application and reflection.

### Alignment with Bloom’s Taxonomy

The quiz questions generated span cognitive levels—ranging from factual recall (e.g., identifying modules) to higher-order analysis (e.g., debugging configuration problems), aligning with Bloom’s taxonomy to support deep learning.

## Benefits

* 📚 Personalized learning aligned with lab content
* ⚙️ Automation of formative assessment generation
* ⬆️ Real-time interaction and feedback
* 🌐 Scalable across labs and topics
* 📊 Trackable via DynamoDB for progress insights

---

## Project Task Summary

| Task Description                                                  | Status      |
| ----------------------------------------------------------------- | ----------- |
| Design and implementation of Streamlit client for lab interaction | ✅ Completed |
| Upload and parse full lab notes as quiz input                     | ✅ Completed |
| Implement POST /ask endpoint integration with SQS and Lambda      | ✅ Completed |
| Agent-based routing and quiz generation via Bedrock Claude        | ✅ Completed |
| Store quiz response in DynamoDB with timestamp                    | ✅ Completed |
| Implement GET /get-answer for quiz retrieval                      | ✅ Completed |
| Render dynamic quiz in Streamlit with markdown and interactivity  | ✅ Completed |
| Polling logic with timeout and API fallback                       | ✅ Completed |
| Error handling and raw request/response display                   | ✅ Completed |
| Pedagogical framework integration (Bloom’s taxonomy, scaffolding) | ✅ Completed |
| Add dashboard and learner profiling features                      | ⏳ To Do     |
| Integrate secure login and quiz history versioning                | ⏳ To Do     |
| Add difficulty-level tagging for adaptive learning                | ⏳ To Do     |
| Design And Implement LabHInt Agent                                | ⏳ To Do     |
| Design and Implement CodeReview Agent                             | ⏳ To Do     |
| Integrtion and Testing                                            | ⏳ To Do     |

---

## Future Enhancements

* 🌟 Difficulty-level tagging and adaptive scaffolding
* 🧠 Learner model integration for profiling and sequencing
* 📊 Dashboard analytics for instructors
* 🔒 Secure login and version-controlled quiz history

## Conclusion

The lab-based adaptive learning architecture presented here effectively bridges practical lab engagement with personalized formative assessment. Powered by AWS services and generative AI, it supports scalable, timely, and pedagogically grounded learning experiences in secure coding education.

---

## Appendix A: Streamlit Client Design

The Streamlit frontend is designed to provide a seamless and interactive user experience for secure logging lab quizzes.

### Features:

* File Upload: Users upload lab notes, solutions, original code.
* Lab Selection: Dropdowns for lab and step selection.
* Quiz Generation: Button triggers API to generate quiz.
* Quiz Display: Dynamically renders questions, options, correct answers, and explanations.
* Feedback: Real-time status indicators and error alerts.
* Developer Insights: Shows raw API requests, responses, polling status.

### Design Screenshot (placeholder):

```
[ Sidebar ]
| Lab File Uploads
| Lab and Step Selection
| User ID Input
| Generate Quiz Button

[ Main Panel ]
| Title and Metadata
| Interactive Quiz Questions with Expanders
| Success and Error Notifications
```

---

## Appendix B: Model Throttling and SQS Architecture

### Purpose

To handle load balancing and ensure scalable, asynchronous processing of quiz generation requests while preventing Bedrock model overuse.

### Architecture Flow

```
[ Streamlit Client ]
   |
   | → API Gateway (POST /ask)
   |
   ↓
[ SQS Queue: SecureCodingRAGQueue ]
   → Decouples user request from backend processing
   → Prevents direct throttling issues to Bedrock Claude
   ↓
[ Lambda Worker Function ]
   → Processes each message with delay/retry/backoff as needed
   → Sends prompts to Bedrock Claude
   ↓
[ DynamoDB Storage ]
   → Persists response with topic/agent/question/response/timestamp
```

### Throttling Mitigation

* Uses SQS to buffer bursts of concurrent quiz generation requests.
* Worker Lambda function handles retries and rate-limiting behavior from Bedrock Claude.
* Future upgrade can include concurrency limits, Dead Letter Queue (DLQ), and exponential backoff.

---

## Appendix C: Multiagent Collaboration

This system is architected to support multiple agents with distinct responsibilities by routing each quiz generation request through a general-purpose **worker Lambda function** that orchestrates downstream agents like `sc-labquiz-gen`.

### Workflow:

```
[ Streamlit Client ]
   |
   | → API Gateway (POST /ask)
   |   Payload:
   |   {
   |     "topic": "Practical 5",
   |     "agent": "sc-labquiz-gen",
   |     "question": "<lab notes>"
   |   }
   ↓
[ Amazon SQS: SecureCodingRAGQueue ]
   → Stores message asynchronously
   ↓
[ Worker Lambda Function ]
   ├─ Parses agent field from payload
   ├─ Forwards lab notes to `sc-labquiz-gen` prompt template
   ├─ Sends request to Bedrock Claude
   └─ Stores result in DynamoDB for retrieval
```

### Message Passing and Exception Handling

* Messages are passed using JSON structure via SQS to worker Lambda.
* The worker parses payload and forwards context to specific agent.
* If downstream processing (e.g., Claude response) is invalid or fails:

  * Worker Lambda **raises an exception**, which prevents SQS message deletion.
  * This causes the message to **reappear after the visibility timeout**, triggering **automatic retry**.
  * Exception details are logged via CloudWatch for debugging and traceability.

### Exception Handling & Retry Workflow

```
[ Streamlit Client ]
   |
   | POST /ask → API Gateway
   ↓
[ Amazon SQS: SecureCodingRAGQueue ]
   |
   | → Delivers message to:
   ↓
[ Worker Lambda Function ]
   |
   | try:
   |   result = agent_handler(...)
   |   if result is valid:
   |       save to DynamoDB
   |   else:
   |       raise Exception("Invalid result")
   |
   | except Exception:
   |   → Logs error to CloudWatch
   |   → Lambda fails without deleting message
   ↓
[ SQS Visibility Timeout ]
   |
   | Message becomes visible again
   | if receive count < maxReceiveCount
   ↓
[ Lambda Retry ]
   |
   | Retry attempt via re-invocation
   ↓
[ Dead Letter Queue (DLQ) ]
   | → After max retries, message sent here for review
```

---

## Appendix D: Agent Prompting

Each agent (e.g., `sc-labquiz-gen`) is designed with a specific prompt template, tuned for the expected task. The system routes input lab content into these prompts, which are structured for optimal performance by the Bedrock Claude model.

### Example Prompt Structure (for sc-labquiz-gen):

```
System Prompt:
You are an educational assistant helping generate secure coding quizzes.

User Prompt:
Here are lab notes for Practical 5 on secure logging:
---
<lab notes content>
---

Please generate 10 multiple-choice questions. Each question should include:
- question
- 4 choices
- correct answer
- explanation

Format the response as JSON.
```

> Agents can be extended or re-prompted in future to handle hints, feedback, or scenario classification.

---

## Appendix E: Visibility and Monitoring for Tuning

To ensure operational reliability, SQS and Lambda settings must be continuously monitored and tuned. This appendix describes the key parameters and dashboards for observability.

### Key Metrics

* **SQS ApproximateNumberOfMessagesVisible**: Backlog indicator.
* **Lambda Duration**: Helps fine-tune timeout.
* **Lambda Throttles and Errors**: Detect concurrency bottlenecks.
* **DynamoDB Write/Read Throttling**: Reveal capacity under/overuse.

### Dashboard Design (CloudWatch)

| Metric                        | Threshold         | Action                                  |
| ----------------------------- | ----------------- | --------------------------------------- |
| SQS Visible Messages > 50     | High backlog      | Add concurrency or increase visibility  |
| Lambda Errors > 0             | Alert immediately | Review logs, update exception handling  |
| Lambda Duration > 25 sec avg  | Too slow          | Optimize prompt or increase timeout     |
| DynamoDB Write Throttling > 0 | Capacity issue    | Switch to on-demand or scale throughput |

### Tuning Guidelines

* **SQS Visibility Timeout**: Set longer than expected Lambda execution (e.g., 45–60 sec).
* **Lambda Timeout**: Slightly higher than average model generation time.
* **Retries**: Keep `maxReceiveCount` to 3–5 before DLQ.
* **Dead Letter Queue (DLQ)**: Ensure all failed messages are logged and reviewed.

A CloudWatch composite dashboard combines these metrics with alarm thresholds and automatic notifications for robust monitoring.

## Appendix F: Backend CDK Deployment Summary
The backend infrastructure is provisioned using AWS CDK (Cloud Development Kit) and deploys a fully serverless architecture for adaptive lab-based quiz generation. The components include:
[![Watch the 3 miniute video on YouTube](https://img.youtube.com/vi/cNqzzDHiTxs/0.jpg)](https://www.youtube.com/watch?v=cNqzzDHiTxs)
---
🔧 Core Components
Component	Details
API Gateway	REST API with endpoints /ask, /get-answer, /get-history, /presigned-url. CORS enabled. CloudWatch logging with custom access log format and throttling controls.
Lambda Functions	Five core functions: submit, worker, get-answer, get-history, presigned-url, each with defined roles and environment variables.
SQS Queue	RAGQueryQueue for asynchronous decoupling with RAGWorkerDLQ configured for retries and durability.
DynamoDB Table	ResponseTable for storing responses keyed by request_id. PAY_PER_REQUEST mode.
S3 Bucket	Referenced external bucket for presigned URLs and static knowledge base (KB) content.
CloudWatch Alarms	Alarm on RAGWorkerDLQ visibility metric to flag unprocessed failures.
IAM Roles	API Gateway role for log publishing, granular Lambda permissions for SQS, DynamoDB, Bedrock, and S3 access.

🧩 Lambda Role & Integration
Each Lambda function is integrated with its respective API method using LambdaIntegration.

SQS event source is configured on the worker Lambda with batch_size=1 for real-time message processing.

Bedrock Claude model is accessed via IAM permissions (bedrock:*) scoped to the worker function.

🔐 API Gateway Access Logging
The gateway captures detailed logs:

Method, IP, status, protocol, timestamp, caller

Enables traceability and auditing of learning sessions

🔁 Retry Safety
SQS visibility_timeout: 40 seconds

Lambda timeout: 50 seconds

DLQ maxReceiveCount: 5

Ensures graceful failure capture and retry without data loss

🚀 Deployment Outputs
Key information exported via CloudFormation for post-deployment visibility:

Lambda names

API base URL

DLQ and queue URLs

DynamoDB table name

Presigned URL endpoint

This CDK-managed deployment ensures repeatable, scalable infrastructure for adaptive learning services, following modern DevOps and serverless best practices.




## Appendix G: Best Practices for Well-Architected Cloud Application

This system design follows the AWS Well-Architected Framework and includes:

Operational Excellence: Logging, CloudWatch metrics, and alarms for dead-letter queues

Security: IAM policies scoped for each Lambda function, API Gateway CORS

Reliability: DLQ configured for retry safety, batching = 1, throttling controlled via API Gateway

Performance Efficiency: Asynchronous processing using SQS and Bedrock model execution

Cost Optimization: PAY_PER_REQUEST for DynamoDB, S3-based static KBs

Sustainability: Serverless infrastructure eliminates idle compute

Foundation Model on Demand: Bedrock Claude is invoked only when needed by the worker Lambda, optimizing compute resource usage and ensuring timely generation of AI-powered adaptive assessments.

✅ Operational Excellence
CloudWatch Logs and Metrics:

logs.LogGroup(self, "ApiGatewayAccessLogs") creates a dedicated log group.

cw.Alarm(...) on self.dead_letter_queue.metric_approximate_number_of_messages_visible() enables proactive alerting.

Tracing and Debugging:

API Gateway deploy_options enables data_trace_enabled=True, improving request diagnostics.

🔐 Security
IAM Scoped Roles:

add_to_role_policy(iam.PolicyStatement(...)) restricts Bedrock access to only the worker Lambda.

CORS Policy:

add_cors_preflight(allow_origins=apigateway.Cors.ALL_ORIGINS...) ensures secure frontend-backend communication across domains.

🔁 Reliability
Dead Letter Queue (DLQ):

Configured with max_receive_count=5 ensures messages that consistently fail get isolated for inspection.

Retry Behavior:

Exception handling in the Worker Lambda with raise RuntimeError(...) from e ensures visibility and SQS retry after visibility timeout.

⚡ Performance Efficiency
SQS-Based Decoupling:

lambda_event_sources.SqsEventSource(self.rag_queue, batch_size=1) enables efficient asynchronous message processing.

Lambda Timeout Tuning:

timeout=Duration.seconds(50) tuned below SQS visibility of 60 seconds ensures retry-safe logic.

💸 Cost Optimization
DynamoDB Mode:

billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST avoids overprovisioning costs.

Serverless Design:

No idle EC2 instances; everything runs on-demand (Lambda, API Gateway, SQS).

🌱 Sustainability
Serverless Stack:

CDK provisions only what’s needed. Stateless Lambdas scale automatically and turn off when idle.

S3 for Knowledge Base:

s3.Bucket.from_bucket_name(...) reuses existing bucket, avoiding duplication.

## Appendix H

# 🔐 Secure Coding Agents LabHint and CodeReview

This README documents the prompt structures and test cases for the secure coding agents in the Bedrock-powered Lambda system.

---

## 💡 LabHint Agent Prompt

> Guides students with progressive, secure coding hints during labs.

### Prompt Template

```
You are a Lab Hint Assistant helping students with secure coding lab exercises. Your goal is to guide them toward the correct solution by offering progressive, supportive hints — without revealing full answers.

Lab Context:
{{ lab_notes }}

Student Question:
{{ student_question }}

You may refer to the following OWASP Top 10 vulnerabilities:

A01: Broken Access Control – Improper restrictions on what authenticated users are allowed to do.  
A02: Cryptographic Failures – Inadequate protection of sensitive data.  
A03: Injection – Unsanitized input leading to SQL, OS, or other command injections.  
A04: Insecure Design – Lack of security controls or flawed security architecture.  
A05: Security Misconfiguration – Default settings, unnecessary features, or improper permissions.  
A06: Vulnerable and Outdated Components – Use of unsupported or vulnerable software.  
A07: Identification and Authentication Failures – Weak or broken authentication mechanisms.  
A08: Software and Data Integrity Failures – Unsigned or unverified updates or code.  
A09: Security Logging and Monitoring Failures – Missing or insufficient logging.  
A10: Server-Side Request Forgery (SSRF) – Server fetches a remote resource without proper validation.

Instructions:
1. Understand the student’s question.
2. Give a concise, helpful hint without showing the solution.
3. If relevant, connect it to an OWASP category.
4. End with: “Would you like another hint or clarification?”

Format:
**Hint:** <your hint>  
**Related Concept (if applicable):** <OWASP reference>  
**Would you like another hint or clarification?**
```

### Sample Test Case

**Input:**
```json
{
  "lab_notes": "Use parameterized queries to avoid SQL injection when storing comments.",
  "student_question": "Can I just concatenate the user input into the SQL query string?"
}
```

**Expected Output:**
```
Hint: It’s safer to use parameterized queries to prevent SQL injection. Concatenating input directly into SQL queries is risky.

Related Concept: A03: Injection – user input is not sanitized

Would you like another hint or clarification?
```

---

## 🔍 Code Review Agent Prompt

> Reviews submitted code for security vulnerabilities and gives OWASP-aligned feedback.

### Prompt Template

```
You are a secure coding review assistant. Your task is to review the student’s submitted code snippet for vulnerabilities and provide constructive feedback, based on secure coding practices and the OWASP Top 10.

Student Question (includes code snippet and context):
{{ student_question_with_code }}

Instructions:
1. Identify security issues, referencing OWASP Top 10.
2. Suggest improvements with explanation and sample fixes.
3. End with a general secure coding tip.

Format:
1. Identified Issues:
2. Suggested Fix:
3. Secure Coding Tip:
```

### Sample Test Case

**Input:**
```json
{
  "student_question_with_code": "Here's my login code:\n\napp.post('/login', (req, res) => {\n  const u = req.body.user;\n  const p = req.body.pass;\n  db.query(`SELECT * FROM users WHERE username = '${u}' AND password = '${p}'`, ...);\n});"
}
```

**Expected Output:**
```
1. Identified Issues:
- A03: Injection – User input is directly injected into SQL.

2. Suggested Fix:
- Use parameterized queries: db.query("SELECT * FROM users WHERE username = ? AND password = ?", [u, p], ...);

3. Secure Coding Tip:
Always sanitize and validate user input using trusted libraries or ORM frameworks.
```

---

## 🧠 OWASP Top 10 Agent Prompt

> Answers technical questions about OWASP vulnerabilities with examples and mitigation.

### Prompt Template

```
You are a secure coding expert answering questions about the OWASP Top 10. Use clear, actionable explanations with examples and mitigation strategies.

Student Question:
{{ student_question }}

Instructions:
1. Identify the OWASP category involved.
2. Explain the vulnerability clearly.
3. Give a real-world example or analogy.
4. Share mitigation techniques.

Format:
- Category:
- Explanation:
- Example:
- Mitigation:
```

### Sample Test Case

**Input:**
```json
{
  "student_question": "What is the problem with storing raw passwords in a user table?"
}
```

**Expected Output:**
```
Category: A02: Cryptographic Failures

Explanation: Storing raw (plaintext) passwords exposes users to credential theft if the database is leaked.

Example: A breach that leaks your DB will reveal users' passwords in plain text.

Mitigation: Always hash passwords with bcrypt or Argon2 before storing them.
```

## Appendix I


# 🎙️ AI-Narrated Just-in-Time Tutorial Video Generator

This module transforms Markdown-based lab tutorials into narrated tutorial videos using AWS services like Polly, Lambda, and S3. It is designed to help lecturers provide dynamic, accessible learning materials based on quiz analytics and topic difficulty.

## 🚀 Features

- Upload `.md` lab tutorials via Streamlit
- Convert to speech using Amazon Polly
- Render synchronized video (audio + static slide or animated text)
- Upload to S3 using presigned URLs
- Optionally publish to YouTube
- Triggered on `.md` upload or update in S3 (via EventBridge)

---

## 🛠️ System Architecture

```mermaid
graph TD
  A[Streamlit Upload (.md)] -->|Presigned PUT| B[S3 Bucket: tutorials/]
  B -->|S3 PutObject Event| C[EventBridge Rule]
  C --> D[Lambda: NarrationGenerator]
  D --> E[Amazon Polly (voice)]
  D --> F[FFMPEG video render]
  F --> G[S3 Upload (presigned PUT)]
  G -->|Optional| H[YouTube API Upload]
```

---

## 📁 Folder Structure

```
📦backend/
 ┣ 📜lambda_narrate_video.py
 ┣ 📜ffmpeg_script.sh
 ┗ 📜polly_utils.py

📦frontend/
 ┗ 📜streamlit_app.py

📄 README.md
```

---

## 📦 Prerequisites

- AWS CLI configured
- FFmpeg layer or binary accessible in Lambda
- Streamlit >= 1.20
- IAM roles for S3, Polly, and Lambda

---

## 🔧 Lambda Environment Variables

| Variable Name   | Description                          |
|----------------|--------------------------------------|
| VOICE_ID        | Polly voice to use (e.g., `Joanna`) |
| OUTPUT_BUCKET   | S3 bucket to store generated videos |
| REGION          | AWS region (e.g., `us-east-1`)      |

---

## 🧪 Local Test (Lambda)

```bash
python lambda_narrate_video.py --input tutorial.md --voice Joanna
```

---

## 🎛️ Streamlit Usage

```bash
streamlit run frontend/streamlit_app.py
```

Features:
- Upload tutorial.md
- Preview video player
- "Generate Video" triggers backend API
- "Upload to YouTube" if desired

---

## 🔐 Permissions and IAM

Minimum IAM policy for Lambda:

```json
{
  "Effect": "Allow",
  "Action": [
    "polly:SynthesizeSpeech",
    "s3:PutObject",
    "s3:GetObject",
    "s3:PutObjectAcl"
  ],
  "Resource": "*"
}
```

---

## 🎓 Pedagogical Value

- **Multimodal learning**: Supports visual + auditory engagement
- **Just-in-time creation**: Videos only generated when new tutorials are added
- **Scalable**: Auto-triggers and AWS-native pipeline
- **Integrates**: Directly into Streamlit + quiz difficulty analytics

---

## 📌 To Do

- [ ] Slide-by-slide video output
- [ ] Highlight syncing with narration
- [ ] YouTube metadata editor
- [ ] Viewer analytics dashboard

---

## 📬 Contact

For integration help or educational use cases: `edtech-support@example.edu`
