variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used to prefix/tag resources"
  type        = string
  default     = "f1-api"
}

variable "environment" {
  description = "Environment name, used in tags"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to spread public/private subnets across"
  type        = number
  default     = 2
}

variable "container_port" {
  description = "Port the Flask app listens on inside the container (matches the Dockerfile's gunicorn bind)"
  type        = number
  default     = 5000
}

variable "image_tag" {
  description = "Tag of the image in ECR to run (pushed by the deploy workflow or manually)"
  type        = string
  default     = "latest"
}

variable "ecs_task_cpu" {
  description = "Fargate task vCPU units (256 = .25 vCPU)"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of running tasks"
  type        = number
  default     = 1
}

variable "db_name" {
  description = "Postgres database name"
  type        = string
  default     = "f1api"
}

variable "db_username" {
  description = "Postgres master username"
  type        = string
  default     = "f1api"
}

variable "db_password" {
  description = "Postgres master password. Pass via TF_VAR_db_password or a tfvars file that is never committed."
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "db_skip_final_snapshot" {
  description = "Skip the final RDS snapshot on destroy. Leave true for a throwaway/demo environment, set false once this holds real data."
  type        = bool
  default     = true
}

variable "cloudfront_public_key_pem" {
  description = <<-EOT
    PEM-encoded RSA public key (2048-4096 bit) used to verify CloudFront
    signed URLs/cookies. Generate a matching private/public keypair with:
      openssl genrsa -out cloudfront-signer.pem 2048
      openssl rsa -pubout -in cloudfront-signer.pem -out cloudfront-signer-public.pem
    Keep the private key out of this repo and out of state — it's only
    used by scripts/sign_cloudfront_url.py to mint signed URLs, never by
    Terraform or the app itself.
  EOT
  type        = string
}

variable "cloudfront_price_class" {
  description = "CloudFront price class"
  type        = string
  default     = "PriceClass_100"
}
