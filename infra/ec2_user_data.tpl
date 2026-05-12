#!/bin/bash
# Example user-data script to install podman and run containers (requires images in a registry)
set -e

yum update -y
yum install -y podman

# Example: pull images (replace with your registry/image names)
# podman login --username USER --password-stdin REGISTRY
# podman pull REGISTRY/yourorg/cloudgallery-backend:latest
# podman pull REGISTRY/yourorg/cloudgallery-frontend:latest

# Run backend
# podman run -d --name cloudgallery-backend -e CLOUDGALLERY_BUCKET=${bucket} -p 5005:5005 REGISTRY/yourorg/cloudgallery-backend:latest

# Run frontend
# podman run -d --name cloudgallery-frontend -p 80:80 REGISTRY/yourorg/cloudgallery-frontend:latest

echo "User-data script finished"
