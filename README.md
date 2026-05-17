# SHL Assessment Recommender

A conversational recommendation API for SHL assessments built using FastAPI, TF-IDF retrieval, and Docker deployment.

---

# Overview

This project implements a multi-turn conversational recommendation system for SHL assessments.

The system:
- accepts conversational hiring requirements
- recommends relevant SHL assessments
- asks clarification questions when requirements are vague
- refines recommendations across multiple turns
- handles comparison questions
- applies conversational guardrails
- returns structured JSON responses

The application is fully stateless and optimized for lightweight deployment.

---

# Live Deployment

## Live API

```text
https://shl-assessment-recommender-26lr.onrender.com
```

---

## Swagger API Documentation

```text
https://shl-assessment-recommender-26lr.onrender.com/docs
```

---

# Features

## Conversational Assessment Recommendations

Supports:
- role-based recommendations
- skill-based recommendations
- multi-turn refinement
- clarification handling
- grounded SHL recommendations

---

## Clarification Handling

The system asks follow-up questions when the request lacks sufficient hiring context.

### Example

User:
```text
We need assessments.
```

Assistant:
```text
Could you describe the role or skills you are hiring for?
```

---

## Recommendation Refinement

The system updates recommendations dynamically as requirements evolve.

### Example

User:
```text
Add simulation-based assessments.
```

Assistant:
```text
Updated shortlist including simulation-based assessments.
```

---

## Assessment Comparisons

Supports direct comparison flows between SHL products.

### Example

User:
```text
What's the difference between DSI and Safety & Dependability 8.0?
```

Assistant:
```text
DSI is a general safety and dependability instrument, while Safety & Dependability 8.0 is calibrated specifically for manufacturing and industrial workforces.
```

---

## Guardrails

The system refuses:
- legal advice
- immigration advice
- political advice
- unrelated off-topic consulting

### Example

User:
```text
Does this legally satisfy HIPAA compliance?
```

Assistant:
```text
Those are legal compliance questions outside what I can advise on.
```

---

# Architecture

## High-Level Flow

```text
User Query
   ↓
Conversation Routing Logic
   ↓
TF-IDF Retrieval
   ↓
Recommendation Formatting
   ↓
JSON API Response
```

---

# Technical Design

## Retrieval System

The project uses:
- TF-IDF vectorization
- cosine similarity retrieval
- lightweight metadata ranking

The retrieval pipeline is optimized for:
- fast startup
- deterministic recommendations
- low memory usage
- free-tier deployment compatibility

---

## Why TF-IDF Instead of Embeddings/FAISS

The SHL catalog is relatively small and domain-specific.

A lightweight TF-IDF approach was selected because it:
- avoids heavyweight embedding downloads
- reduces deployment complexity
- minimizes RAM consumption
- improves startup speed
- works reliably on Render free tier infrastructure
- provides stable deterministic retrieval for constrained catalogs

This design prioritizes:
- robustness
- simplicity
- deployment reliability
- maintainability

---

# Tech Stack

| Component | Technology |
|---|---|
| Backend API | FastAPI |
| Retrieval Engine | Scikit-learn TF-IDF |
| Similarity Search | Cosine Similarity |
| Deployment | Render |
| Containerization | Docker |
| Language | Python 3.11 |

---

# Project Structure

```text
api/
├── routes.py
├── schemas.py

core/
├── agent.py
├── catalog.py
├── embeddings.py
├── retriever.py

data/
├── catalog.json
├── catalog_meta.pkl
├── tfidf_matrix.pkl
├── tfidf_vectorizer.pkl

Dockerfile
Render.yaml
requirements.txt
runtime.txt
build_catalog.py
main.py
README.md
```

---

# API Endpoints

# GET /

Root endpoint.

## Response

```json
{
  "message": "SHL Assessment Recommender API is running"
}
```

---

# GET /health

Health-check endpoint.

## Response

```json
{
  "status": "ok"
}
```

---

# POST /chat

Main conversational recommendation endpoint.

---

## Example Request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring graduate financial analysts"
    }
  ]
}
```

---

## Example Response

```json
{
  "reply": "Here are recommended SHL assessments for this role.",
  "recommendations": [
    {
      "name": "SHL Verify Interactive – Numerical Reasoning",
      "url": "https://www.shl.com/",
      "test_type": "A"
    }
  ],
  "end_of_conversation": false
}
```

---

# Response Schema

```json
{
  "reply": "string",
  "recommendations": [
    {
      "name": "string",
      "url": "string",
      "test_type": "string"
    }
  ],
  "end_of_conversation": false
}
```

---




# Testing Strategy

The system was tested against:
- clarification scenarios
- recommendation refinement flows
- comparison questions
- leadership hiring workflows
- healthcare bilingual hiring scenarios
- contact-center screening flows
- graduate hiring flows
- legal/off-topic refusal cases

---

# Key Behavioral Capabilities

## Supported Behaviors

- clarification questioning
- recommendation refinement
- conversational memory through message history
- comparison handling
- recommendation filtering
- guardrail enforcement

---

# Stateless Design

The API is fully stateless.

Every `/chat` request contains:
- current user message
- previous conversation history

No server-side conversation memory is stored.

Benefits:
- easier scaling
- reproducibility
- simpler deployment
- lower infrastructure complexity

---

# Challenges Faced

Earlier iterations used:
- sentence transformers
- FAISS
- hosted LLM APIs

These introduced:
- deployment instability
- larger Docker images
- higher RAM usage
- slower startup
- Python compatibility issues

The architecture was simplified into a lightweight TF-IDF retrieval first design for improved robustness and free-tier compatibility.

---

# Future Improvements

Potential future improvements include:
- hybrid retrieval (TF-IDF + embeddings)
- reranking models
- multilingual retrieval
- evaluation pipelines
- confidence scoring
- semantic recommendation explanations

---

