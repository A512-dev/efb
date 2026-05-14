#!/bin/bash

# Create directories
mkdir -p nginx
mkdir -p docker
mkdir -p scripts
mkdir -p monitoring/grafana
mkdir -p ssl
mkdir -p doc  # Documentation directory for guides, diagrams, etc.

# Create empty files
touch nginx/skydeck.conf
touch docker/backend.Dockerfile
touch docker/frontend.Dockerfile
touch docker/docker-compose.yml
touch scripts/deploy.sh
touch scripts/backup.sh
touch scripts/restore.sh
touch monitoring/prometheus.yml
touch .env.example
touch .gitignore

echo "Infra structure created. Now add README.md manually."