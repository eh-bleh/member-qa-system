# Member QA System

A question-answering API service that answers natural language questions about member data using Claude AI.

## 🚀 Live Deployment (Railway)

Your deployed API is publicly accessible here:

**Base URL:** `https://member-qa-system-production-8c5a.up.railway.app`

### Endpoints

**Health Check**
```
GET /health
```

**Ask a Question**
```
POST /ask
```
```json
{
  "question": "When is Layla planning her trip to London?"
}
```

## 📁 Project Structure

```
member-qa-system/
├── main.py                          # Main FastAPI application
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container configuration
├── docker-compose.yml               # Docker Compose setup
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
├── QUICKSTART.md                    # Quick setup guide
├── index.html                       # Web testing interface
├── test_api.py                      # Automated test script
├── analyze_data.py                  # Data analysis tool (Bonus 2)
├── example_usage.py                 # Usage examples
└── data_analysis_results.json       # Output of dataset analysis
```

## Overview

This service retrieves member messages from the provided `/messages` API and uses Claude (Anthropic's AI model) to interpret natural language questions and extract relevant answers.

**The system:**
- Fetches messages from: `https://november7-730026606190.europe-west1.run.app/messages`
- Sends both the message dataset and the user's question to Claude
- Returns a structured JSON answer

## API Endpoints

### POST /ask

**Request Body:**
```json
{
  "question": "When is Layla planning her trip to London?"
}
```

**Response:**
```json
{
  "answer": "Layla mentions planning her trip to London in June 2024."
}
```

**Example Questions:**
- "How many cars does Vikram Desai have?"
- "What are Amira's favorite restaurants?"
- "List all the members who have sent messages."

## Setup & Deployment

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your Anthropic API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. **Run the server:**
   ```bash
   uvicorn main:app --reload --port 8080
   ```

4. **API will be available at:**
   ```
   http://localhost:8080
   ```

### Docker Deployment

**Build and run:**
```bash
docker build -t member-qa-system .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY="your-api-key" member-qa-system
```

### Deploying on Railway (Used in this project)

1. Create a Railway project
2. Select "Deploy from GitHub" and choose this repo
3. Set environment variable: `ANTHROPIC_API_KEY=your-key`
4. Railway builds and deploys automatically
5. **Live URL:** `https://member-qa-system-production-8c5a.up.railway.app`

### Deploy to Other Platforms

The Dockerfile supports deployment to:
- Google Cloud Run
- AWS ECS / Fargate
- Heroku (Container Registry)
- Render
- DigitalOcean App Platform

## Testing

### Command Line
```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
```

### Python Test Suite
```bash
python test_api.py
```

### Web Testing Interface

Open `index.html` in your browser.

**Features:**
- Example buttons
- Real-time answers
- Response time metrics
- Error and debug panel

## Architecture

The system follows a simple pipeline:

1. Receive question
2. Fetch all member messages
3. Construct LLM prompt with:
   - dataset
   - user question
4. Claude extracts relevant information
5. Structured JSON answer returned

## ⚠️ Known Limitation — Upstream /messages API Instability

The assignment API:
```
https://november7-730026606190.europe-west1.run.app/messages
```

returns `307 Temporary Redirect` to `/messages/`

But the redirected endpoint frequently returns inconsistent HTTP errors:
- 400 Bad Request
- 401 Unauthorized
- 402 Payment Required
- 403 Forbidden
- 405 Method Not Allowed

Because this is upstream behavior, the QA service handles it gracefully by returning a friendly `"answer": "Failed to fetch member data…"`, while staying compliant with the assignment.

## Bonus 1: Alternative Approaches Considered

### ✔ 1. LLM-Based Approach (Chosen)

Uses Claude to extract answers from the dataset.

**Pros:**
- Flexible natural language understanding
- Minimal engineering overhead
- No schema or pattern writing

**Cons:**
- Reliant on API
- Higher latency

### 2. Traditional NLP + Pattern Matching

**Pros:**
- Fast
- Deterministic

**Cons:**
- Brittle
- Requires heavy manual rule-writing

### 3. Embedding-Based Semantic Search

**Pros:**
- Good semantic matching

**Cons:**
- Requires extra pipeline for extraction

### 4. Fine-Tuned Model

**Pros:**
- Fast, predictable

**Cons:**
- Requires labeled dataset

### 5. Text-to-SQL Pipeline

**Pros:**
- Efficient for structured questions

**Cons:**
- Requires a SQL database + schema mapping

### Why LLM Approach Was Chosen

- Handles varied question types
- Works well for small datasets
- No effort needed to maintain rules → faster development
- Best option given the assignment constraints

## Bonus 2: Data Insights & Anomalies

`analyze_data.py` performs structural and semantic checks on the dataset.

### Findings:

**Redirect Errors**
- `/messages` → 307 redirect
- redirected endpoint unpredictably returns 400/401/402/403/405

**Duplicate Messages**
- Several message entries appear multiple times.

**Missing Fields**
- Some entries lack author names, timestamps, or text.

**Inconsistent Formats**
- Dates appear in mixed formats (ISO vs informal).

**Edge-case Values**
- Some fields contain null or empty strings unexpectedly.

A machine-generated report is saved at: `data_analysis_results.json`

## Technologies Used

- **FastAPI** — backend framework
- **Claude (Anthropic API)** — natural language reasoning
- **httpx** — async HTTP client
- **Docker** — containerization
- **Python 3.11** — runtime
- **Railway** — production deployment
