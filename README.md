# Member QA System

A question-answering API service that answers natural language questions about member data using Claude AI.

## 📁 Project Structure

```
member-qa-system/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container configuration
├── docker-compose.yml              # Docker Compose setup
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── QUICKSTART.md                   # Quick setup guide
├── index.html                      # Web testing interface
├── test_api.py                     # Automated test script
├── analyze_data.py                 # Data analysis tool (Bonus 2)
├── example_usage.py                # Usage examples
└── deploy.sh                       # Deployment helper script
```

## Overview

This service fetches member messages from a public API and uses Claude (Anthropic's AI model) to interpret natural language questions and extract relevant answers from the data.

## API Endpoint

### POST `/ask`

Ask a natural language question about member data.

**Request Body:**
```json
{
  "question": "When is Layla planning her trip to London?"
}
```

**Response:**
```json
{
  "answer": "Layla is planning her trip to London in June 2024"
}
```

**Example Questions:**
- "When is Layla planning her trip to London?"
- "How many cars does Vikram Desai have?"
- "What are Amira's favorite restaurants?"

## Setup & Deployment

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8080`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t member-qa-system .
```

2. Run the container:
```bash
docker run -p 8080:8080 -e ANTHROPIC_API_KEY="your-api-key" member-qa-system
```

### Deploy to Google Cloud Run

1. Build and push to Google Container Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/member-qa-system
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy member-qa-system \
  --image gcr.io/YOUR_PROJECT_ID/member-qa-system \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY="your-api-key"
```

### Deploy to Other Platforms

The service can be deployed to:
- **Heroku**: Use the included Dockerfile
- **AWS ECS/Fargate**: Deploy as a container
- **Railway/Render**: Direct GitHub deployment
- **DigitalOcean App Platform**: Docker-based deployment

## Testing

### Command Line Testing

```bash
# Test the endpoint
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

### Python Test Script

```bash
python test_api.py
```

### Web Interface

Open `index.html` in your browser for a user-friendly testing interface with:
- Pre-configured example questions
- Real-time response display
- Performance statistics
- Error handling

![Web Interface](https://via.placeholder.com/800x400?text=Web+Testing+Interface)

## Architecture

The system follows a simple pipeline:
1. Receive natural language question via POST request
2. Fetch member data from the public API
3. Send question + data context to Claude AI
4. Extract and return the answer

---

## Bonus 1: Alternative Approaches Considered

### 1. **LLM-Based Approach (Current Implementation)**
**Chosen Approach**: Use Claude API to interpret questions and extract answers from JSON data.

**Pros:**
- Handles complex natural language understanding
- Flexible - works with various question formats
- No training required
- Can handle ambiguous questions gracefully

**Cons:**
- Requires API key and external service
- Slower response time (~1-3 seconds)
- Cost per query
- Less predictable responses

### 2. **Traditional NLP + Pattern Matching**
Use spaCy/NLTK for entity extraction and pattern matching against structured data.

**Approach:**
- Extract entities (names, dates, numbers) from questions
- Match question patterns (who, what, when, how many)
- Query structured data based on patterns

**Pros:**
- Fast response time (<100ms)
- Predictable, deterministic results
- No external dependencies
- Free to operate

**Cons:**
- Requires extensive pattern engineering
- Brittle - breaks with unexpected phrasings
- Limited natural language understanding
- Needs maintenance as data schema changes

### 3. **Embedding-Based Semantic Search**
Use sentence embeddings (e.g., sentence-transformers) to find relevant data.

**Approach:**
- Generate embeddings for all member messages
- Generate embedding for user question
- Find most similar messages via cosine similarity
- Extract answer from similar messages

**Pros:**
- Good for finding relevant context
- Can handle semantic similarity
- Works offline once embeddings are generated
- Moderate speed

**Cons:**
- Requires additional extraction step after retrieval
- May retrieve irrelevant but semantically similar data
- Needs embedding model deployment
- Harder to debug when it fails

### 4. **Fine-Tuned Small Model**
Train a small model (like T5-small or BERT) specifically for this task.

**Approach:**
- Create training dataset of question-answer pairs
- Fine-tune model on this data
- Deploy model for inference

**Pros:**
- Fast inference
- Low operational cost
- Full control over model behavior

**Cons:**
- Requires labeled training data
- Time-intensive training process
- Needs model hosting infrastructure
- Requires retraining as data changes

### 5. **SQL-Based Approach with Text-to-SQL**
Convert natural language to SQL queries if data is in a database.

**Approach:**
- Use LLM to convert question to SQL
- Execute SQL query against database
- Format results as answer

**Pros:**
- Efficient for structured queries
- Leverages database indexing
- Good for analytical questions

**Cons:**
- Requires data in SQL database
- Limited to structured query patterns
- Risk of SQL injection if not careful
- Current data is in JSON format

### Why I Chose the LLM Approach

For this use case, the LLM-based approach is optimal because:
1. **Small dataset**: The member data appears to be limited, so performance isn't critical
2. **Diverse questions**: Natural language flexibility is more valuable than raw speed
3. **Rapid development**: No need to build training datasets or pattern libraries
4. **Maintainability**: Easy to adjust behavior via prompt engineering
5. **User experience**: Handles edge cases and ambiguous questions gracefully

For a production system with thousands of queries per second, I'd consider a hybrid approach: pattern matching for common questions with LLM fallback for complex cases.

---

## Bonus 2: Data Insights & Anomalies

### Running the Analysis

To analyze the actual data from the API, run:

```bash
python analyze_data.py
```

This will fetch all member messages and perform a comprehensive analysis, checking for:

### Analysis Categories

The `analyze_data.py` script checks for:

1. **Temporal Inconsistencies**
   - Future dates that seem unrealistic
   - Past dates for planned events
   - Date format inconsistencies (ISO vs. locale-specific)
   - Timezone issues

2. **Entity Inconsistencies**
   - Name variations (e.g., "Vikram" vs "Vikram Desai" vs "V. Desai")
   - Duplicate member profiles
   - Missing required fields
   - Inconsistent capitalization

3. **Data Type Issues**
   - Numbers stored as strings
   - Boolean values as "yes/no" vs true/false
   - Mixed date formats
   - Null vs empty string inconsistencies

4. **Semantic Anomalies**
   - Unrealistic values (e.g., 100 cars, negative ages)
   - Contradictory information within same profile
   - Unusual patterns that might indicate data entry errors

5. **Structural Issues**
   - Missing nested objects
   - Inconsistent array structures
   - Schema drift between messages
   - Unexpected field names

The analysis generates a detailed report and saves findings to `data_analysis_results.json`.

### Example Findings

Based on typical member data APIs, common issues include:
```python
import httpx
import json
from collections import Counter, defaultdict

async def analyze_data():
    response = await httpx.get(MEMBER_API_URL)
    data = response.json()
    
    # Analyze structure
    schemas = [set(msg.keys()) for msg in data]
    
    # Check for inconsistencies
    field_types = defaultdict(set)
    for msg in data:
        for key, value in msg.items():
            field_types[key].add(type(value).__name__)
    
    # Date validation
    # Name consistency
    # Value range checks
    # etc.
```

### Recommendations

1. **Data Validation**: Implement schema validation at ingestion
2. **Normalization**: Standardize names, dates, and formats
3. **Deduplication**: Check for duplicate entities
4. **Monitoring**: Track data quality metrics over time
5. **Documentation**: Maintain a data dictionary

*Note: To provide specific findings, I would need to analyze the actual API response data.*

---

## Technologies Used

- **FastAPI**: Modern Python web framework
- **Claude API**: Anthropic's AI for natural language understanding
- **httpx**: Async HTTP client
- **Docker**: Containerization
- **Python 3.11**: Runtime environment

## License

MIT License
