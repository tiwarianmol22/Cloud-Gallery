# CloudGallery — File Summary

This document contains concise one-line descriptions for the main files and folders in the CloudGallery repository.

- `frontend/index.html` — Main static HTML page providing the user interface, upload controls, album view, and the full-size image modal.
- `frontend/script.js` — Client-side logic: uploads images, calls backend `/upload`, `/albums`, and `/image` endpoints, builds the responsive gallery, and handles image interactions.
- `frontend/styles.css` — UI styling: color theme, responsive grid, container shapes, hover/loading animations, and modal styles.
- `frontend/Dockerfile` — Builds a lightweight container image for serving the frontend static site in containerized deployments.
- `backend/app.py` — Flask API that handles image upload, S3 interactions (upload/list/presigned or proxy), and serves image endpoints with CORS and error handling.
- `backend/Dockerfile` — Dockerfile to containerize the Flask backend for deployment with Podman/Docker.
- `backend/requirements.txt` — Python dependency list (Flask, boto3, python-dotenv, etc.) required to run the backend.
- `docker-compose.yml` — Compose configuration to run backend (and frontend if wired) together locally for development.
- `README.md` — Project documentation with setup, run, and deployment instructions (local and AWS).
- `infra/main.tf` — Terraform configuration that provisions cloud resources (e.g., S3 bucket, optional EC2) for deployment.
- `infra/variables.tf` — Terraform variable definitions used by the infra templates.
- `infra/outputs.tf` — Terraform outputs that expose created resource identifiers (bucket name, IPs).
- `infra/ec2_user_data.tpl` — EC2 user-data template to bootstrap container runtime and start the app on instance launch.
- `scripts/local_up.sh` — Local helper script to build and run containers (podman/docker) for quick development runs.
- `.env.example` — Template environment file showing required variables (AWS keys, bucket name, options) for local configuration.
- `.env` — Local environment file (not committed) containing actual AWS credentials and app config for development.
- `.gitignore` — Git ignore rules to exclude sensitive files (like `.env`, `venv/`) and build artifacts.

If you'd like this exported as a Word (`.docx`) file as well, I can generate `docs/file-summary.docx` and place it in the repository.
