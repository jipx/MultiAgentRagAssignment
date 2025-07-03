
## 🧠 SC Lab Quiz Generation Flow

### 📤 Generate Quiz Flow (`POST /ask` → `SQS` → `sc-labquiz-gen`)

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
   |   "question": "Generate MCQs for secure logging"
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

### 📥 Load Quiz Flow (`GET /get-answer`)

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
