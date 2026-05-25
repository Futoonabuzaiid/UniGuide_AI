from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import ask_uniguide


app = FastAPI(title="UniGuide AI Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "UniGuide AI Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ask")
def ask(request: AskRequest):
    result = ask_uniguide(request.question)

    return {
        "question": request.question,
        "answer": result["answer"],
        "docs": result["docs"]
    }