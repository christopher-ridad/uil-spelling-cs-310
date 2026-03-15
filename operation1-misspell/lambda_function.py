#
# Lambda function to generate a single misspelling of a word using the Google Gemini API.
#
# The word is passed to the function in the body of the request, in
# a dictionary-like object in JSON format:
#
# {
#   "word": "accommodate"
# }
#
# The response is a dictionary-like object in JSON format, with
# status code of 200 (success) or 500 (server-side error). The data
# is a single plausible misspelling:
#
# {
#   "message": "...",
#   "data": {"misspelling": "accomodate"}
# }
#

import json
import os
import google.genai as genai

def lambda_handler(event, context):
  try:
    print("**Call to misspell...")

    #
    # the user has sent us one parameter:
    #   1. the word to misspell
    #
    # The parameter is coming in the body of the
    # request, in JSON format.
    #
    print("**Accessing request body")

    if "body" not in event:
      return {
        'statusCode': 400,
        'body': json.dumps({"message": "request has no body", "data": {}})
      }

    body = json.loads(event["body"])  # parse the json

    if "word" not in body:
      return {
        'statusCode': 400,
        'body': json.dumps({"message": "request has no key 'word'", "data": {}})
      }

    word = body["word"]

    print("word:", word)

    #
    # call Gemini to generate a single plausible misspelling:
    #
    print("**Calling Gemini API")

    gemini_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=gemini_key)

    prompt = (
      f"Generate exactly one realistic, plausible misspelling of the word '{word}'. "
      f"It should look like a common student mistake, not random characters. "
      f"Respond only with the misspelled word as a plain string, no explanation, no extra text."
    )

    response = client.models.generate_content(
      model="gemini-2.5-flash",
      contents=prompt
    )

    print("**Gemini response:", response.text)

    misspelling = response.text.strip()

    print("**Responding to client...")

    body = {
      "message": "success",
      "data": {"misspelling": misspelling}
    }

    return {
      'statusCode': 200,
      'body': json.dumps(body)
    }

  #
  # exception handling:
  #
  except Exception as e:
    print("**Exception")
    print("**Message:", str(e))

    body = {
      "message": str(e),
      "data": {}
    }

    return {
      'statusCode': 500,
      'body': json.dumps(body)
    }