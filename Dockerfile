FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.16 /uv /bin/uv
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
RUN python -m persistence.generate && python -m persistence.sensitivity && python -m explorer.build
EXPOSE 8000
CMD ["uvicorn", "assistant.server:app", "--host", "0.0.0.0", "--port", "8000"]
