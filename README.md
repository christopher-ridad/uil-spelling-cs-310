# UIL Spelling Study App

Backend web service for a UIL competitive spelling study tool. Manages ~1,500 official UIL spelling words, tracks student performance, and generates intelligent quiz content.

**Team:** Christopher Ridad, Joanna Echeverri Porras, Joseph Pennella  
**Stack:** AWS API Gateway, Lambda, RDS (PostgreSQL), Google Gemini API

---

## Base URL
```
https://...us-east-1.amazonaws.com/prod
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
  "message": "success",
  "data": {
    "words": ["accommodate", "pneumonia", "necessary"]
  }
}
```

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