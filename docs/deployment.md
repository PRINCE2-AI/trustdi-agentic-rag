# Deployment Guide

TrustDI Agentic RAG can run locally through Python or through Docker.

## Local API

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

## Local Dashboard

```bash
streamlit run app/ui.py
```

## Docker API

```bash
docker build -t trustdi-agentic-rag .
docker run --env-file .env -p 8000:8000 trustdi-agentic-rag
```

## Docker Compose

```bash
docker compose up --build
```

Services:

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| Dashboard | http://localhost:8501 |

## Notes

- Start from `.env.example` and create `.env` before running Docker Compose.
- OpenAI explanations and external KB lookup are optional for local demos.
- The `data/` directory is mounted as a local volume for sample CSVs and run outputs.
