# CloudGallery — containerized photo sharing microservice

This repository contains a minimal containerized photo-sharing service (frontend + backend) that stores images in AWS S3.

What's included
- `backend/` — Flask API that accepts uploads and lists albums (uploads objects to S3).
- `frontend/` — Static single-page app that uploads images and lists albums.
- `docker-compose.yml` — local compose to run backend + frontend.
- `infra/` — Terraform scaffold to create an S3 bucket and an EC2 user-data example (templates).

Quick local run (using podman)

1. Set AWS credentials and bucket name as environment variables. For local testing you can create a bucket in AWS or use an existing bucket.

```bash
export AWS_ACCESS_KEY_ID=YOUR_KEY
export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
export AWS_DEFAULT_REGION=us-east-1
export CLOUDGALLERY_BUCKET=your-bucket-name
export CLOUDGALLERY_REGION=us-east-1
```

2. Build and run with podman-compose (or docker-compose)

```bash
# build images
podman-compose build
# run
podman-compose up
```

If you don't have podman-compose, you can use `podman build` and `podman run` directly. The backend listens on port 5005 and the frontend is served on port 8080.

Notes on deployment to AWS
- Use the Terraform files in `infra/` to create an S3 bucket and (optionally) an EC2 instance. The EC2 user-data contains an example script to install podman and pull/run containers, but you'll need to push your built images to a registry (Docker Hub / ECR) first.
- For production, prefer private S3 objects + presigned URLs and proper IAM roles.

Next steps / extras you might want
- Add authentication and per-user albums.
- Use an image-processing microservice (lambda or ECS task) for resizing.
- Automate image builds/push to ECR/GitHub Container Registry and use ECS or EKS for container orchestration.

Monitoring with Prometheus & Grafana
-----------------------------------
This repository includes an optional monitoring stack (Prometheus + Grafana).

To start the monitoring stack together with the app, run:

```bash
# Start app and monitoring together
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build
```

- Prometheus UI: http://localhost:9090
- Grafana UI: http://localhost:3000 (default admin/admin)

Grafana is pre-provisioned with a Prometheus datasource and a basic dashboard located at `http://localhost:3000` once the stack is up.

The Prometheus config is in `prometheus/prometheus.yml` and will scrape the backend at `backend:5005/metrics`.

