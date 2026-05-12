terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "gallery" {
  bucket = var.bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name = "cloudgallery-bucket"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.gallery.id
}

# Example EC2 instance. This is optional — the user_data installs podman and shows how to run containers.
resource "aws_instance" "gallery_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = {
    Name = "cloudgallery-ec2"
  }

  user_data = templatefile("${path.module}/ec2_user_data.tpl", { bucket = var.bucket_name })

  # NOTE: Security group, key_name and IAM role must be set in your environment or expanded here.
}
