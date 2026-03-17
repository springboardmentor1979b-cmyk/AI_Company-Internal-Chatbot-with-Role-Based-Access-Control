#!/bin/bash
set -e
echo "🐉 Dragon Intel — Starting up..."

echo "📦 Seeding database..."
python -m backend.init_users

echo "📄 Preprocessing documents..."
python -m preprocessing.preprocess_all

echo "🔢 Building vector embeddings..."
python -m vector_db.embedding_engine

echo "🚀 Starting API server..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
