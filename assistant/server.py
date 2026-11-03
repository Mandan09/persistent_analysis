"""Serves the explorer with a streaming /ask endpoint for the assistant."""
import json

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from assistant.agent import ROOT, labels, stream

app = FastAPI()


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[tuple[str, str]] = Field(default=[], max_length=20)


# The explorer page.
@app.get("/")
def page():
    return FileResponse(ROOT / "explorer" / "explorer.html")


# Streams the answer as JSON lines: text deltas, then the checked reply with source titles.
@app.post("/ask")
def answer(q: Question):
    def lines():
        for part in stream(q.question, q.history):
            if isinstance(part, str):
                yield json.dumps({"delta": part}) + "\n"
            else:
                yield json.dumps({"done": part.model_dump(), "sources": {c: labels()[c] for c in part.citations}}) + "\n"
    return StreamingResponse(lines(), media_type="application/x-ndjson")
