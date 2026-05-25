
# UniGuide AI

UniGuide AI is an AI-powered university assistant designed to answer University of Jeddah questions using Retrieval-Augmented Generation (RAG), semantic search, and multilingual NLP.

The system supports both Arabic and English queries and provides grounded responses based on official university data, FAQs, and processed university documents.

---

# Features

- AI-powered university assistant
- Arabic and English support
- RAG-based intelligent question answering
- Semantic search using vector embeddings
- FAISS vector database integration
- FastAPI backend
- React + Vite frontend
- Real-time conversational interface
- Smart retrieval and grounded response generation
- University-focused assistant with admission and academic support

---

# Supported Topics

UniGuide AI can answer questions related to:

- Admission requirements
- Majors and colleges
- Preparatory year
- Fees and tuition
- Diplomas and tracks
- University services
- Emergency information
- Registration and academic information

---

# System Architecture

The project consists of:

## Frontend
- React + Vite user interface
- Multilingual chat interface
- Real-time chat experience

## Backend
- FastAPI REST API
- RAG retrieval pipeline
- Query preprocessing and normalization
- Semantic retrieval using FAISS
- Gemini-based response generation

## AI Pipeline
- SentenceTransformer embeddings
- Hybrid retrieval system
- FAISS similarity search
- Gemini API integration
- Multilingual NLP support

---

# RAG Pipeline Workflow

1. Collect university data and FAQs
2. Clean and preprocess documents
3. Chunk documents into smaller sections
4. Generate embeddings using multilingual-e5-large
5. Store embeddings in FAISS vector index
6. Retrieve relevant chunks based on user question
7. Generate grounded answer using Gemini API

---

# Technologies Used

## Backend
- Python
- FastAPI
- FAISS
- Sentence Transformers
- Hugging Face
- Gemini API

## Frontend
- React
- Vite
- JavaScript
- CSS

## AI & NLP
- multilingual-e5-large
- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Vector Embeddings
- NLP

---

# Example Questions

## Arabic
- كم رسوم السنة التأهيلية؟
- ما تخصصات كلية الحاسب؟
- ما شروط القبول؟

## English
- What are the admission requirements?
- How much is the preparatory year fee?
- What majors are available in the College of Computer Science?

---

# API Endpoints

## Health Check
```bash
GET /health
````

## Ask Question

```bash
POST /ask
```

Example Request:

```json
{
  "question": "What are the admission requirements?"
}
```


# Installation

## Backend

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Frontend

```bash
npm install
npm run dev
```

---


The system includes:

* Arabic chat interface
* English chat interface
* Real-time AI responses
* RAG retrieval pipeline visualization

---

# Goal

UniGuide AI aims to improve students’ access to university information through an intelligent conversational experience powered by modern AI, NLP, and RAG technologies.

---
