#!/usr/bin/env bash
set -euo pipefail

# Helper to build and run the app locally with podman-compose (or docker-compose).
# Usage: copy .env.example to .env and fill in values OR ensure ~/.aws/credentials is configured.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo ".env not found — copying .env.example to .env (edit with your values)"
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example — please edit .env with your AWS credentials or remove keys to use ~/.aws credentials.";
  else
    echo "No .env.example available. Please create a .env with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure ~/.aws.";
  fi
fi

echo "Building images..."
podman-compose build

echo "Bringing up containers (foreground). Use Ctrl-C to stop or run 'podman-compose up -d' to daemonize."
podman-compose up
