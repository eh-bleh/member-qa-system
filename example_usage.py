#!/usr/bin/env python3
"""
Example usage of the Member QA System API
"""

import asyncio
import json

import httpx

# Use deployed Railway URL
API_URL = "https://member-qa-system-production-8c5a.up.railway.app"


async def ask_question(question: str) -> str:
    """Send a question to the Member QA System and return the answer text."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_URL}/ask",
                headers={"Content-Type": "application/json"},
                content=json.dumps({"question": question}),
            )

        if response.status_code == 200:
            data = response.json()
            return data.get("answer", "<No 'answer' field in response>")
        else:
            return f"[ERROR] Status {response.status_code}: {response.text}"
    except httpx.RequestError as exc:
        return f"[ERROR] Request failed: {exc}"


async def main() -> None:
    questions = [
        "When is Layla planning her trip to London?",
        "How many cars does Vikram Desai have?",
        "What are Amira's favorite restaurants?",
        "Who mentioned traveling to Paris?",
        "What hobbies do the members have?",
        "Which members like Italian food?",
        "When is someone's birthday?",
        "Who owns a Tesla?",
    ]

    print("=" * 80)
    print("Member QA System - Example Queries")
    print("=" * 80)
    print()

    for question in questions:
        print(f"Q: {question}")
        answer = await ask_question(question)
        print(f"A: {answer}")
        print("-" * 80)
        print()

        # Be nice to the LLM / upstream API
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
