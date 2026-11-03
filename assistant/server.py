"""Serves the explorer with a working /ask endpoint for the assistant."""
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from assistant.agent import ROOT, ask

app = FastAPI()


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[tuple[str, str]] = Field(default=[], max_length=20)


# The explorer page.
@app.get("/")
def page():
    return FileResponse(ROOT / "explorer" / "explorer.html")


# Answers one methodology question.
@app.post("/ask")
def answer(q: Question):
    return ask(q.question, q.history)
