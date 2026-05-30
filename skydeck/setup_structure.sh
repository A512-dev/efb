#!/bin/bash

# Create directories
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/api/api_v1/endpoints
mkdir -p app/services
mkdir -p app/utils
mkdir -p app/middleware
mkdir -p alembic
mkdir -p tests
mkdir -p doc  # Documentation directory for detailed guides, diagrams, etc.

# Create empty files
touch app/main.py
touch app/core/config.py
touch app/core/security.py
touch app/core/database.py
touch app/core/deps.py
touch app/models/user.py
touch app/models/session.py
touch app/models/form.py
touch app/models/submission.py
touch app/models/manual.py
touch app/schemas/user.py
touch app/schemas/auth.py
touch app/schemas/form.py
touch app/schemas/submission.py
touch app/api/api_v1/api.py
touch app/api/api_v1/endpoints/auth.py
touch app/api/api_v1/endpoints/users.py
touch app/api/api_v1/endpoints/forms.py
touch app/api/api_v1/endpoints/submissions.py
touch app/api/api_v1/endpoints/manuals.py
touch app/services/auth_service.py
touch app/services/sync_service.py
touch app/services/watermark_service.py
touch app/services/storage_service.py
touch app/services/audit_service.py
touch app/utils/encryption.py
touch app/utils/logger.py
touch app/utils/helpers.py
touch app/middleware/audit_log.py
touch app/middleware/auth_middleware.py
touch .env.example
touch requirements.txt
touch Dockerfile
touch docker-compose.yml
touch .gitignore

echo "Backend structure created. Now add README.md manually."