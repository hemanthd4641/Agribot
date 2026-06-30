# Raitha mitra API Documentation

This document provides comprehensive details for the Raitha mitra API endpoints. The API allows you to interact with the multi-agent CrewAI system to get highly structured, professional agricultural advice.

## Base URL

All API endpoints are relative to the base URL of the deployed Flask application. For local development, the base URL is:

```
http://127.0.0.1:5000
```

## Authentication

All API requests require a Groq API key configured on the server side via the `GROQ_API_KEY` environment variable.

## Endpoints

### 1. Chat Interaction (Text, Voice, Image)

Send a text message, voice recording, or image and receive a structured consultation report from the CrewAI orchestration layer.

**Endpoint:** `POST /chat`

**Request Body (FormData/JSON):**

| Field    | Type   | Required | Description                                      |
|----------|--------|----------|--------------------------------------------------|
| `text`   | string | No*      | The user's text query related to agriculture.    |
| `audio`  | File   | No*      | Audio file (WAV, MP3) with speech.               |
| `image`  | File   | No       | Image file for disease detection (JPG, PNG).     |

*\* Either `text` or `audio` is required.*

**Success Response (200 OK):**

```json
{
  "text": "## Weather Summary\n...\n## Crop Recommendation\n...",
  "voice": "/static/audio/response_12345.wav",
  "transcription": "What is the best time to plant wheat?" // Only if audio was sent
}
```

---

### 2. Live Agent Status (SSE/Polling)

Poll this endpoint while a `/chat` request is processing to get the live status of the active AI Agents (e.g. Weather Analyst, Crop Specialist).

**Endpoint:** `GET /chat/status`

**Success Response (200 OK):**

```json
[
  {
    "agent": "Weather Analyst",
    "status": "completed"
  },
  {
    "agent": "Crop Specialist",
    "status": "completed"
  }
]
```

---

### 3. Clear Chat History

Clear the conversation history for the current session.

**Endpoint:** `POST /chat/clear`

**Success Response (200 OK):**

```json
{
  "status": "ok",
  "message": "Conversation cleared."
}
```

---

### 4. Health Check

Verify that the API and Redis are running and healthy.

**Endpoint:** `GET /health`

**Success Response (200 OK):**

```json
{
  "status": "healthy",
  "redis": "connected",
  "timestamp": "2026-06-30T10:00:00.000000"
}
```

---

## Domain Guard

Raitha mitra implements a strict Domain Guard. Any request unrelated to agriculture (e.g., medical, financial, political) will be intercepted before reaching the LLM and immediately rejected with an error message in the `text` field.

## Rate Limiting

Requests are rate limited. Exceeding the limit will result in a **429 Too Many Requests** response.