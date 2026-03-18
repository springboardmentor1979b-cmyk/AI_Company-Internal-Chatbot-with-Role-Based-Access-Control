FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Only seed DB at build time (no ML models needed)
RUN python -m backend.init_users

# At runtime: preprocess + embed + start server
CMD ["sh", "-c", "python -m preprocessing.preprocess_all && python -m vector_db.embedding_engine && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
