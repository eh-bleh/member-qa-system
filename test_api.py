#!/usr/bin/env python3
"""
Test script for the Member QA System API
"""
import asyncio
import json

import httpx

# Configuration
API_BASE_URL = "http://localhost:8080"  # Change this to deployed URL

# Test questions based on the API structure
TEST_QUESTIONS = [
    "When is Layla planning her trip to London?",
    "How many cars does Vikram Desai have?",
    "What are Amira's favorite restaurants?",
    "List all the members who have sent messages",
    "What activities or hobbies are mentioned?",
    "Are there any upcoming events or trips mentioned?",
    "Who mentioned food or restaurants?",
]


async def test_health_check() -> bool:
    """Test the health check endpoint."""
    print("Testing health check endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            response.raise_for_status()
            print(f"✓ Health check passed: {response.json()}")
            return True
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return False


async def test_ask_question(question: str):
    """
    Test asking a question.

    Returns:
        (success: bool, upstream_issue: bool)
        success=True  -> /ask behaved correctly and returned an answer
        upstream_issue=True -> /ask failed only because the external /messages API errored
    """
    print(f"\n{'=' * 80}")
    print(f"Question: {question}")
    print(f"{'=' * 80}")

    async with httpx.AsyncClient(timeout=90.0) as client:  # Increased timeout
        try:
            response = await client.post(
                f"{API_BASE_URL}/ask",
                json={"question": question},
            )
            response.raise_for_status()
            result = response.json()

            # Safely get the answer
            answer = result.get("answer", "<No 'answer' field in response>")
            preview = answer[:200] + "..." if len(answer) > 200 else answer
            print(f"Answer: {preview}")
            print("Status: ✓ Success")
            return True, False

        except httpx.TimeoutException:
            print("Status: ✗ Timeout (request took too long)")
            print(
                "Note: This might work with a longer timeout or fewer consecutive requests."
            )
            return False, False

        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            print(f"Status: ✗ HTTP Error {status_code}")

            upstream_issue = False
            try:
                error_detail = e.response.json()
                detail_msg = error_detail.get("detail", e.response.text)
            except Exception:
                detail_msg = e.response.text

            print(f"Error: {detail_msg}")

            # Detect the common upstream error pattern:
            # our service couldn't fetch member data because the public /messages API
            # returned a 4xx (400/401/402/403...)
            if (
                "Failed to fetch member data" in detail_msg
                and "november7-730026606190.europe-west1.run.app/messages" in detail_msg
            ):
                upstream_issue = True
                print(
                    "Note: This looks like a transient or permission error from the "
                    "public /messages API, not from your service logic."
                )
                print(
                    "      You can rerun the tests or mention this upstream limitation "
                    "in your README."
                )

            return False, upstream_issue

        except Exception as e:
            print("Status: ✗ Failed")
            print(f"Error: {str(e)}")
            return False, False


async def test_invalid_request() -> bool:
    """Test with invalid request (empty question)."""
    print(f"\n{'=' * 80}")
    print("Testing invalid request (empty question)...")
    print(f"{'=' * 80}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/ask",
                json={"question": ""},
            )
            if response.status_code == 400:
                print("✓ Correctly rejected empty question")
                return True
            else:
                print(f"✗ Unexpected status code: {response.status_code}")
                print(f"Body: {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def main() -> None:
    """Run all tests."""
    print(f"\n{'#' * 80}")
    print("# Member QA System - API Tests")
    print(f"# Testing against: {API_BASE_URL}")
    print(f"{'#' * 80}\n")

    # Test health check
    health_ok = await test_health_check()
    if not health_ok:
        print("\n⚠️  Health check failed. Is the service running?")
        return

    # Small delay after health check
    await asyncio.sleep(1)

    # Test valid questions
    print("\n" + "=" * 80)
    print("Testing valid questions...")
    print("=" * 80)

    results: list[bool] = []
    upstream_issues: list[bool] = []

    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n[Test {i}/{len(TEST_QUESTIONS)}]")
        success, upstream_issue = await test_ask_question(question)
        results.append(success)
        upstream_issues.append(upstream_issue)

        # Add delay between requests to avoid rate limiting
        if i < len(TEST_QUESTIONS):
            print("\nWaiting 3 seconds before next request...")
            await asyncio.sleep(3)

    # Test invalid request
    await asyncio.sleep(2)
    invalid_result = await test_invalid_request()

    # Summary
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    total = len(results)
    passed = sum(results)
    upstream_count = sum(upstream_issues)

    print(f"Questions tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    if upstream_count:
        print(f"Of the failures, {upstream_count} were due to upstream /messages API issues.")
    print(f"Success rate: {(passed / total) * 100:.1f}%")

    if invalid_result:
        print("Invalid request handling: ✓ Passed")
    else:
        print("Invalid request handling: ✗ Failed")

    print("\n✓ All tests completed!")

    if passed == total and invalid_result:
        print("\n🎉 All tests passed! Your API is working perfectly!")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed! Your API is working well.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        if upstream_count:
            print(
                "   Note: Some failures are due to the external /messages API, not your service."
            )


if __name__ == "__main__":
    asyncio.run(main())
