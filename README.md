# UIL Spelling Study App

Backend web service for a UIL competitive spelling study tool. Manages ~1,500 official UIL spelling words, tracks student performance, and generates intelligent quiz content.

**Team:** Christopher Ridad, Joanna Echeverri Porras, Joseph Pennella  
**Stack:** AWS API Gateway, Lambda, RDS (PostgreSQL), Google Gemini API

---

## Base URL
```
https://qk7g2mpk1h.execute-api.us-east-1.amazonaws.com/test
```

---

## Endpoints

### POST /misspell

Generates a single plausible misspelling of a given word.

**Request**
```json
{
  "word": "accommodate"
}
```

**Response**
```json
{
  "message": "success",
  "data": {
    "misspelling": "accomodate"
  }
}
```

---

### POST /quiz

Returns a weighted list of words for a quiz session, prioritizing words the user has struggled with.

Adaptive scoring algorithm:
```
score = 1 - (correct / total_attempts)
```

Words are sampled probabilistically without replacement using `score` as weight.
If a user has no history rows yet (cold start), the endpoint returns the first `N` words from `words` (ordered by `word`).

**Request**
```json
{
  "userId": "u123",
  "count": 10
}
```

**Response**
```json
{
  "words": ["accommodate", "pneumonia", "necessary"]
}
```

**Route verification (stub mode)**
- Set Lambda environment variable `QUIZ_USE_STUB=true`
- Call `POST /quiz` with any valid `userId` and `count`
- Lambda returns a fixed stub list slice, confirming API Gateway route wiring before database setup

---

### GET /stats/{userId}

Returns practice statistics for a given user.

**Response**
```json
{
  "message": "success",
  "data": {
    "streak": 5,
    "totalPracticed": 340,
    "accuracy": 0.74
  }
}
```

---

## Error Responses

All endpoints return the following structure on error:
```json
{
  "message": "error description",
  "data": {}
}
```

| Status Code | Meaning |
|---|---|
| 400 | Client error: missing required fields |
| 500 | Server error |

---

## Setup

### 1. Database
- Provision a PostgreSQL RDS instance on AWS
- Run the provided SQL schema files to create the `words` and `user_history` tables
- Run the provided script to insert the 1,500 UIL words

### 2. Lambda Functions
- Create three Lambda functions in AWS (Python 3.14 runtime): `misspell`, `quiz`, `stats`
- Upload each corresponding source file
- Create a Lambda layer with the required dependencies and attach to each function:
  - `misspell` needs `google-genai`
  - `quiz` and `stats` need `psycopg2-binary`
- Set the following environment variables on each Lambda:
  - `RDS_HOST` — RDS instance endpoint
  - `RDS_DB` — database name
  - `RDS_USER` — database username
  - `RDS_PASS` — database password
  - `GEMINI_API_KEY` — only needed on the `misspell` Lambda
  - `QUIZ_USE_STUB` — set to `true` only for temporary `/quiz` route verification

### 3. API Gateway
- Create a REST API with three routes pointing to each Lambda:
  - `POST /misspell`
  - `POST /quiz`
  - `GET /stats/{userId}`
- Deploy the API and note the invoke URL

### 4. Client
- Install dependencies as needed, including `py -m pip install requests`
- Update `baseurl` in the client script with the API Gateway invoke URL
- Run with `py client.py`
