"""
Lambda function to select quiz words using adaptive weighted sampling

The request is passed in the body of the event, in JSON format:

  {
    "userId": "u123",
    "count": 10
  }

The words for the quiz are selected based on adaptive weighted sampling. 
The response is JSON with either {count}selected words or an error message:

  {
    "message": "success",
    "data": {
      "words": ["word1", "word2", ...]
    }
  }

Words with higher score are sampled more often. For users with no history,
the Lambda returns the first N words in deterministic word-list order.
"""

import json
import random
import inspect
import logging

from tenacity import retry, stop_after_attempt, wait_exponential

from build_rds import data_to_rds as rds

# computes the per-word accuracy given the user id
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
)
def get_word_scores(user_id):
    dbConn = None
    dbCursor = None

    try:
        dbConn = rds.get_dbConn()
        dbCursor = dbConn.cursor()

        sql = """
            SELECT
                words.word,
                COALESCE(
                    1.0 - (
                        CAST(user_history.correct AS DECIMAL(10,4))
                        / NULLIF(user_history.total_attempts, 0)
                    ),
                    1.0
                ) AS score
            FROM words
            LEFT JOIN user_history
                ON user_history.word_id = words.word_id
                AND user_history.user_id = %s
            ORDER BY words.word_id;
        """

        dbCursor.execute(sql, (user_id,))
        rows = dbCursor.fetchall()

        scores = []

        for word, score in rows:
            numeric_score = float(score) if score is not None else 1.0
            scores.append({
                "word": word,
                "score": numeric_score
            })

        return scores
    except Exception as err:
        logging.error("lambda_handler.get_word_scores():")
        logging.error(str(err))
        raise
    finally:
        try:
            dbCursor.close()
        except:
            pass
        try:
            dbConn.close()
        except:
            pass


# gets {count} words with weighted random sampling without replacement using each item's score
def weighted_sample(words, count):
    try:
        rng = random.Random()

        remaining = list(words)
        chosen = []
        remaining_weight = sum(max(0.0, word["score"]) for word in remaining)
        picks = min(count, len(remaining))

        for _ in range(picks):
            # if all remaining words have 0 weight, get random words from remaining words
            if remaining_weight <= 0.0:
                num_left = picks - len(chosen)
                random_words = rng.sample(remaining, num_left)
                for word in random_words:
                    chosen.append(word["word"])
                break

            threshold = rng.random() * remaining_weight
            accumulated = 0.0
            chosen_idx = 0

            for idx, word in enumerate(remaining):
                accumulated += max(0.0, word["score"])
                if accumulated >= threshold:
                    chosen_idx = idx
                    break
            
            remaining_weight -= max(0.0, remaining[chosen_idx]["score"])
            chosen_word = remaining.pop(chosen_idx)
            chosen.append(chosen_word["word"])

        return chosen
    except Exception as err:
        logging.error("lambda_handler.weighted_sample():")
        logging.error(str(err))
        raise


# Select {count} quiz words using cold-start fallback or weighted sampling
def choose_quiz_words(word_scores, count):
    try:
        count = min(count, len(word_scores))
        # if there are no words, return empty list
        if len(word_scores) == 0:
            return []

        # check if user has history, if not return first N words in deterministic order
        user_has_history = False
        for word in word_scores:
            print(f"word: {word['word']}, score: {word['score']}")
            if word["score"] < 1.0:
                user_has_history = True
                break
        if not user_has_history:
            return [word["word"] for word in word_scores[:count]]

        return weighted_sample(word_scores, count)
    except Exception as err:
        logging.error("lambda_handler.choose_quiz_words():")
        logging.error(str(err))
        raise


# Lambda entry point for POST /quiz.
# Input: event (API Gateway event dict), context (Lambda context, unused).
# Output: API Gateway response dict with statusCode and JSON body.
def lambda_handler(event, context):
    try:
        print("**Call to quiz...")
        print("**Accessing request body")

        # validate request body
        if "body" not in event:
            raise ValueError("request has no body")
        body = json.loads(event["body"])
        if "userId" not in body:
            raise ValueError("request has no key 'userId'")
        if "count" not in body:
            raise ValueError("request has no key 'count'")

        # extract and validate parameters
        user_id = str(body["userId"]).strip()
        count = int(body["count"])
        if user_id == "":
            raise ValueError("userId cannot be empty")
        if count <= 0:
            raise ValueError("count must be > 0")

        print("userId:", user_id)
        print("count:", count)

        print("**Selecting words...")
        scores = get_word_scores(user_id)
        words = choose_quiz_words(scores, count)

        print("**Responding to client...")

        body = {
            "message": "success",
            "data": {
                "words": words
            }
        }

        return {
            'statusCode': 200,
            'body': json.dumps(body)
        }
    # client error as we were not called correctly
    except ValueError as e:
        print("**Exception")
        print("**Message:", str(e))

        body = {
            "message": str(e),
            "data": {}
        }

        return {
            'statusCode': 400,
            'body': json.dumps(body)
        }
    # server side error 
    except Exception as e:
        logging.error("lambda_handler():")
        logging.error(str(e))

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