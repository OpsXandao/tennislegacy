#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Mata processos anteriores nas portas 8000 e 5173
echo "Liberando portas..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true

# Backend
echo "Iniciando backend..."
cd "$ROOT"
source .venv/bin/activate
uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Aguarda backend subir
sleep 2

# Frontend
echo "Iniciando frontend..."
cd "$ROOT/Front"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Backend : http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Pressione Ctrl+C para encerrar tudo."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM
wait
