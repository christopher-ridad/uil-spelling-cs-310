"""
Local client for testing operation2 quiz Lambda.

Prompts for userId and count, builds request event, calls
lambda_handler directly, and prints the full response.
"""

import json
import os
import sys

# Ensure imports like build_rds.* resolve when run from operation2-quiz.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lambda_function import lambda_handler


# Keep console output focused on error messages instead of tracebacks.
sys.tracebacklimit = 0

# Build an API Gateway proxy event with a JSON body
def build_event(user_id, count):
    body = {
        "userId": user_id,
        "count": count,
    }
    return {
        "body": json.dumps(body)
    }

# Prompt user input, call lambda_handler, print all returned data
def quiz_client():
    user_id = input("User ID? ").strip()
    count_text = input("How many quiz words (count)? ").strip()

    try:
        count = int(count_text)
    except ValueError:
        print("**ERROR: count must be an integer")
        return

    event = build_event(user_id, count)

    print("\nCalling lambda_handler with event:")
    print(json.dumps(event, indent=2))

    response = lambda_handler(event, None)

    print("\nLambda response (full):")
    print(json.dumps(response, indent=2))

    if isinstance(response, dict) and "body" in response:
        try:
            parsed_body = json.loads(response["body"])
            print("\nLambda response body (parsed JSON):")
            print(json.dumps(parsed_body, indent=2))
        except (TypeError, ValueError):
            print("\nLambda response body is not valid JSON:")
            print(response["body"])


if __name__ == "__main__":
    quiz_client()
