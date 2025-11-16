📘 Member QA System

A lightweight question–answering API that interprets natural-language questions about member messages and returns an answer using LLM reasoning over data retrieved from the assignment’s /messages API.

Deployed on Railway for easy public access.

🚀 Live Service

The Member QA API is deployed and publicly accessible here:

Base URL:

https://member-qa-system-production-8c5a.up.railway.app

Endpoints
Method	Path	Description
GET	/health	Health check
POST	/ask	Ask any natural-language question about the member data
Example Usage
curl -X POST "https://member-qa-system-production-8c5a.up.railway.app/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'

🧠 Overview

This project builds a simple API service that:

Retrieves member messages from the public endpoint:
https://november7-730026606190.europe-west1.run.app/messages

Allows users to ask natural-language questions:

Example: “How many cars does Vikram Desai have?”

Sends the retrieved messages + the user’s question to an LLM (Claude via Anthropic API).

Returns a structured answer:

{ "answer": "Vikram Desai has two cars mentioned in his messages." }

📦 Project Structure
member-qa-system/
│
├── main.py                 # FastAPI backend service
├── Dockerfile              # Production container build
├── docker-compose.yml      # Local Docker testing
├── requirements.txt        # Python dependencies
├── analyze_data.py         # Bonus: dataset analysis script
├── example_usage.py        # Client script for asking questions
├── test_api.py             # Automated API test script
├── index.html              # Front-end test UI
├── quickstart.md           # Lightweight dev notes
├── .env.example            # Example environment variables (no secrets)
└── README.md               # You are here

⚙️ Running Locally
1. Install dependencies
pip install -r requirements.txt

2. Add your Anthropic API key

Copy .env.example → .env and fill in:

ANTHROPIC_API_KEY=your_key_here

3. Run the server
uvicorn main:app --reload --port 8080


Check:

http://localhost:8080/health

http://localhost:8080/docs

4. Try with curl
curl -X POST "http://localhost:8080/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"List all members who sent messages"}'

5. Try the frontend

Open:

index.html


Change the API endpoint box to:

http://localhost:8080

🔬 Bonus 1 — Design Notes (Required by assignment)
Approach A — LLM-First (Chosen)

Retrieve all messages from /messages

Generate a structured prompt combining messages + user’s question

Let the LLM infer answers directly

Works well for loosely structured data

Handles fuzzy questions (e.g., “Who likes Italian food?”)

Approach B — Preprocessing into Knowledge Graph

Parse messages into structured fields

Build entities, timelines, events

Query via semantic rules

More deterministic but heavier engineering

Approach C — Embedding Search + Retrieval-Augmented Generation

Embed each message

Search based on user query

Pass relevant chunks to an LLM

More scalable for large datasets, but overkill for this assignment

Why Approach A was chosen

✔ Lightweight
✔ Requires no external DB
✔ Flexible for varied question types
✔ Minimal overhead
✔ Easy to deploy

🔍 Bonus 2 — Data Insights (Automated from analyze_data.py)

While analyzing the dataset from the /messages endpoint, the following anomalies were found:

Redirect & Inconsistent URL behavior

/messages returns 307 Temporary Redirect → /messages/

The redirected endpoint returns various unexpected 4xx errors:

400 Bad Request

401 Unauthorized

402 Payment Required (!!)

403 Forbidden

405 Method Not Allowed

Duplicate messages

Some user messages appear identical or nearly identical.

Date formatting issues

A few timestamps appear missing or incorrectly formatted.

Unexpected field values

Some message objects contain missing or empty fields.

These findings are summarized in data_analysis_results.json.

⚠️ Known Limitation: Upstream /messages API Behavior

This system depends on the public endpoint:

https://november7-730026606190.europe-west1.run.app/messages


During testing, this endpoint consistently redirects to:

http://november7-730026606190.europe-west1.run.app/messages/


The redirected path frequently returns:

400 Bad Request

401 Unauthorized

402 Payment Required

403 Forbidden

405 Method Not Allowed

Empty bodies

These failures originate from the upstream service, not from this QA system.

The /ask endpoint gracefully surfaces these upstream errors by returning a meaningful message inside the "answer" field.

🧪 Local Test Suite

Run:

python3 test_api.py


Tests include:

Health check

Valid question queries

Timeout / error handling

Upstream API behavior detection

Empty-input validation

Because of upstream /messages instability, some tests may pass/fail nondeterministically.
This is documented and expected.

🖥️ Example Usage Script
python3 example_usage.py


This script:

Sends multiple questions

Applies rate-limiting (to avoid LLM throttling)

Prints answers or error messages cleanly

🌐 Production Deployment (Railway)

This backend is hosted on Railway using:

Auto-build from GitHub

Dockerfile-based deployment

Public URL for testing

Environment variable for API key

Steps:

Connect GitHub repository

Set ANTHROPIC_API_KEY under Variables

Railway auto-builds & auto-deploys

Live URL becomes available
