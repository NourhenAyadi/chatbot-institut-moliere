# AI Assistant Chatbot (RAG-Based)

## Overview

This project is a backend system for an AI-powered chatbot based on Retrieval-Augmented Generation (RAG), designed to manage communications for an educational institution (Institut Molière).

The chatbot can answer user questions using custom data sources such as PDF documents, making it suitable for educational platforms, schools, or customer support systems.

It is built using FastAPI and LangChain, and supports both:

* High-speed inference using Llama 3 via Groq
* Local model execution via Ollama

---
## Demo



---

## Key Features

* RAG (Retrieval-Augmented Generation) using PDF documents stored in the `doc/` folder
* Local vector database powered by ChromaDB
* High-performance API built with FastAPI (includes interactive Swagger documentation)
* Simple web interface using Jinja2, HTML, CSS, and JavaScript
* Flexible LLM support (Groq API or local Ollama models)

---

## Use Cases

* Educational chatbot for schools and institutions
* Homework assistance and student support
* FAQ automation for websites
* AI assistant trained on custom documents

---

## Tech Stack

* Python
* FastAPI
* LangChain
* ChromaDB
* Llama 3 (via Groq) / Ollama (local LLM)
* HTML / CSS / JavaScript (frontend)

---

## Requirements

* Python 3.10+
* (Optional) Docker for containerized deployment

---

## Quick Installation (Local Setup)

1. Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd chatbot_moliere
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

* Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

* Add your `GROQ_API_KEY` inside the `.env` file
  (If not provided, the system will fallback to a local Ollama model, which is slower)

---

## Running the Application

### Run locally

```bash
uvicorn main:app --reload --port 8001
```

Access the application:

* Chat interface: http://localhost:8001/
* API documentation (Swagger): http://localhost:8001/docs

---

### Run with Docker

```bash
docker build -t chatbot-moliere .
docker run -d -p 8001:8001 --env-file .env chatbot-moliere
```

---

## API Integration

The chatbot logic is fully accessible via API, making it easy to integrate into any frontend or external platform.

Main endpoint:

```
POST /ask
```

Request body:

```json
{
  "question": "Where is the institute located?"
}
```

Response:

```json
{
  "response": "The Institut Molière is located in Tunis...",
  "type": "RAG"
}
```

---

## Project Structure

* `main.py` — Core FastAPI application and RAG pipeline
* `doc/` — PDF documents used as knowledge base
* `static/` — Static assets (CSS, images)
* `templates/` — HTML templates
* `db/` — ChromaDB vector database

---

## Future Improvements

* Improved user interface
* Multi-language support
* Voice interaction support
* Deployment to cloud platforms

---

## Author

Your Name
ma (créée automatiquement au premier lancement, ignorée dans git).
