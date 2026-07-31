#!/usr/bin/env bash
# =============================================================================
# scripts/setup.sh — developer bootstrap script
# Run once after cloning: bash scripts/setup.sh
# =============================================================================
set -euo pipefail

echo "→ Copying environment file..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  .env created from .env.example"
else
  echo "  .env already exists — skipping"
fi

echo "→ Setting up Python virtual environment..."
cd backend
if [ ! -d .venv ]; then
  python3.12 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt -r requirements-dev.txt --quiet
echo "  Backend dependencies installed"
cd ..

echo "→ Installing frontend dependencies..."
cd frontend
npm ci --silent
echo "  Frontend dependencies installed"
cd ..

echo ""
echo "Setup complete."
echo ""
echo "Start the backend:"
echo "  cd backend && source .venv/bin/activate && python run.py"
echo ""
echo "Start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "Or use Docker Compose:"
echo "  docker compose up --build"
