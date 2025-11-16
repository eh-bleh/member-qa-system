from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Dict, Any
import json

app = FastAPI(title="Member QA System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
# This is the base messages endpoint from the Swagger docs
MEMBER_API_URL = "https://november7-730026606190.europe-west1.run.app/messages"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str


async def fetch_member_data() -> Dict[str, Any]:
    """
    Fetch member messages from the API.
    For this project we just use the first page (default skip=0, limit=100).
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            resp = await client.get(MEMBER_API_URL)
            resp.raise_for_status()
            data = resp.json()

            # Ensure we always return a dict with total + items
            items = data.get("items", []) if isinstance(data, dict) else data
            total = data.get("total", len(items)) if isinstance(data, dict) else len(items)

            return {"total": total, "items": items}

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch member data: {str(e)}",
            )


async def ask_claude(question: str, context: Dict[str, Any]) -> str:
    """Use Claude to answer questions based on member data."""

    # Ensure API key is present
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is not set in the environment.",
        )

    # Extract items from the response
    items = context.get("items", []) or []
    total = context.get("total", len(items))

    # Format messages for better context
    formatted_messages = []
    for item in items:
        msg = {
            "user_name": item.get("user_name"),
            "message": item.get("message"),
            "timestamp": item.get("timestamp"),
        }
        formatted_messages.append(msg)

    context_str = json.dumps(formatted_messages, indent=2)

    prompt = f"""You are a helpful assistant that answers questions about member messages.

I have {total} messages from various members. Here are the messages:

{context_str}

Question: {question}

Please analyze the member messages and provide a direct, concise answer to the question. 

Guidelines:
- If the answer involves dates, provide them in a clear, readable format
- If the answer involves counts, provide the exact number
- If the answer involves lists (like restaurants, hobbies, etc.), list them clearly
- If a member's name is mentioned in the question, try variations (first name only, full name, etc.)
- If the information is not available in the messages, say "I don't have that information in the available messages"
- Be conversational and natural in your response

Answer only with the factual information from the data."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                },
            )
            response.raise_for_status()
            result = response.json()

            # Extract the answer from Claude's response
            content = result.get("content", [])
            if not content or "text" not in content[0]:
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from Claude.",
                )

            answer_text = content[0]["text"]
            return answer_text.strip()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Claude API error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Claude: {str(e)}",
            )


@app.get("/")
async def root():
    """Root endpoint with basic service info."""
    return {
        "status": "healthy",
        "service": "Member QA System",
        "endpoints": {
            "/ask": "POST - Ask questions about member data",
            "/health": "GET - Health check",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """
    Answer natural language questions about member data.

    Example questions:
    - When is Layla planning her trip to London?
    - How many cars does Vikram Desai have?
    - What are Amira's favorite restaurants?
    """
    if not question.question or not question.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Fetch member data
    member_data = await fetch_member_data()

    # Ask Claude to answer the question
    answer = await ask_claude(question.question, member_data)

    return Answer(answer=answer)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
