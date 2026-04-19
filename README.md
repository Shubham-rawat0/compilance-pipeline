# Brand Guardian – Video Compliance Audit Pipeline

A production-oriented backend system that analyzes YouTube videos and determines whether brand advertisements comply with regulatory and policy guidelines. It combines **Azure AI services**, **LangChain**, and **vector search (RAG)** to perform structured compliance audits.

---

## Overview

Brand Guardian ingests a YouTube video, extracts multimodal signals (audio + OCR), retrieves relevant compliance rules from a vector database, and uses an LLM to generate a structured audit report.

### Core capabilities

* YouTube video ingestion
* Multimodal analysis (speech + on-screen text)
* Retrieval-Augmented Generation (RAG)
* Rule-based compliance auditing
* Structured JSON reports (PASS / FAIL)

---

## Architecture

```text
User / Client
      │
      ▼
FastAPI (/audit)
      │
      ▼
LangGraph Workflow
 ├── index_video_node
 │     ├─ Download video
 │     ├─ Upload → Azure Video Indexer
 │     └─ Extract transcript + OCR
 │
 └── audio_content_node
       ├─ Query Vector DB (Azure Search)
       ├─ Retrieve compliance rules
       └─ LLM audit (Azure OpenAI)
              │
              ▼
        Structured Report
```

---

## Tech Stack

* **Backend**: FastAPI
* **Workflow Orchestration**: LangGraph / LangChain
* **LLM**: Azure OpenAI (Chat + Embeddings)
* **Vector DB**: Azure AI Search
* **Video Processing**: Azure Video Indexer
* **Document Processing**: PyPDF + Text Splitters
* **Language**: Python

---

## 📂 Project Structure

```text
backend/
├── src/
│   ├── api/            # FastAPI routes
│   ├── graph/          # LangGraph workflow + nodes
│   ├── services/       # Business logic (video indexer, LLM, etc.)
│   ├── data/           # Compliance PDFs (rules)
│   └── models/         # Pydantic schemas
│
├── indexer.py          # Offline vector DB ingestion
├── main.py             # CLI runner (debug/testing)
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Environment variables

Create a `.env` file:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_CHAT_DEPLOYMENT=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=

AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_API_KEY=
AZURE_SEARCH_INDEX_NAME=

AZURE_VIDEO_INDEXER_KEY=
AZURE_VIDEO_INDEXER_ENDPOINT=
```

---

## Step 1: Index Compliance Documents

Before running the API, build your vector database:

```bash
python indexer.py
```

This will:

* Load PDFs from `/data`
* Split into chunks
* Generate embeddings
* Upload to Azure AI Search

---

##  Step 2: Test via CLI

```bash
python main.py <youtube_url>
```

Useful for:

* debugging workflow
* verifying pipeline output

---

##  Step 3: Run FastAPI

```bash
uvicorn api:app --reload
```

---

##  API Usage

### POST `/audit`

#### Request

```json
{
  "video_url": "https://youtube.com/..."
}
```

#### Response

```json
{
  "session_id": "uuid",
  "video_id": "vid_xxxx",
  "status": "PASS | FAIL",
  "final_report": "Summary...",
  "compliance_results": [
    {
      "category": "Claim Validation",
      "severity": "CRITICAL",
      "description": "Misleading claim detected..."
    }
  ]
}
```

---

##  How It Works

### 1. Video Processing

* Downloads YouTube video
* Uploads to Azure Video Indexer
* Extracts:

  * Transcript (speech)
  * OCR text (on-screen content)

---

### 2. Retrieval (RAG)

* Combines transcript + OCR
* Queries Azure Search
* Retrieves top-K relevant compliance rules

---

### 3. LLM Audit

* Injects rules into system prompt
* Analyzes content
* Outputs strict JSON:

  * violations
  * severity
  * final decision

---

##  Design Notes

* Indexing is **offline** (run separately)
* API is **read/query only**
* Heavy operations can be moved to background workers for production
* Ensure strict JSON parsing from LLM output

---

##  Future Improvements

* Async + background job processing (Celery / queue)
* Streaming responses
* Dashboard UI for reports
* Multi-language support
* Real-time moderation

---

##  Key Concepts

* **RAG (Retrieval-Augmented Generation)**
* **Vector Similarity Search**
* **Multimodal AI (audio + OCR)**
* **LLM-based classification**

---

##  Summary

Brand Guardian is a **scalable compliance auditing system** that bridges:

* unstructured video data
* regulatory knowledge bases
* and LLM reasoning

to produce **automated, explainable compliance decisions**.

---
