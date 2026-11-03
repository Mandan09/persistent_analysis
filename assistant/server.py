"""Serves the explorer with a streaming /ask endpoint for the assistant."""
import json
import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from assistant.agent import ROOT, details, stream

app = FastAPI()
LIMITS = {"ip": (3600, 30), "all": (86400, 500)}
seen = defaultdict(deque)


# Allows 30 questions per visitor per hour and 500 in total per day, so a public link can't run up the bill.
def allow(ip):
    now = time.time()
    for key, (window, cap) in ((ip, LIMITS["ip"]), ("*", LIMITS["all"])):
        while seen[key] and now - seen[key][0] > window:
            seen[key].popleft()
        if len(seen[key]) >= cap:
            return False
    seen[ip].append(now)
    seen["*"].append(now)
    return True


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[tuple[str, str]] = Field(default=[], max_length=20)


# The explorer page.
@app.get("/")
def page():
    return FileResponse(ROOT / "explorer" / "explorer.html")


# The slide deck.
@app.get("/deck")
def deck():
    return FileResponse(ROOT / "deck" / "deck.html")


# Streams the answer as JSON lines: text deltas, then the checked reply with source titles.
@app.post("/ask")
def answer(q: Question, request: Request):
    if not allow(request.headers.get("x-forwarded-for", request.client.host).split(",")[0].strip()):
        raise HTTPException(429, "Too many questions for now. Try again later.")

    def lines():
        for part in stream(q.question, q.history):
            if isinstance(part, str):
                yield json.dumps({"delta": part}) + "\n"
            else:
                yield json.dumps({"done": part.model_dump(), "sources": {c: details()[c] for c in part.citations}}) + "\n"
    return StreamingResponse(lines(), media_type="application/x-ndjson")
