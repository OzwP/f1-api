# AWS deployment (ECS Fargate + RDS + CloudFront)

Provisions:
- A VPC (public subnets for the ALB/NAT, private subnets for ECS tasks and RDS)
- An ECR repository for the app image
- An RDS Postgres instance, reachable only from the ECS tasks
- An ECS Fargate service running the app, behind an ALB that only accepts
  traffic from CloudFront's IP ranges *and* a shared secret header
- A CloudFront distribution in front of the ALB that requires every
  request to carry a valid signed URL or signed cookie (`trusted_key_groups`)
  — this is the access control layer, not just a CDN

See the repo root README's "Deploying" section for the narrative walkthrough.
This file is the quick reference.

## One-time setup

```bash
# 1. Generate the RSA keypair CloudFront will use to verify signed URLs.
#    The private key never goes into Terraform, state, or this repo.
openssl genrsa -out cloudfront-signer.pem 2048
openssl rsa -pubout -in cloudfront-signer.pem -out cloudfront-signer-public.pem

# 2. Copy terraform.tfvars.example -> terraform.tfvars, fill in db_password
#    and paste cloudfront-signer-public.pem's contents into
#    cloudfront_public_key_pem. Or skip the file and pass
#    TF_VAR_db_password / TF_VAR_cloudfront_public_key_pem instead.

terraform init
terraform apply
```

## Building and pushing the image

```bash
aws ecr get-login-password --region <region> \
  | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

docker build -t <ecr_repository_url>:latest ..
docker push <ecr_repository_url>:latest

# Pick up the new image (or set image_tag and terraform apply again)
aws ecs update-service --cluster <ecs_cluster_name> --service <ecs_service_name> --force-new-deployment
```

`.github/workflows/deploy-aws.yml` automates this from CI via `workflow_dispatch`
once the AWS_ROLE_ARN etc. repo variables are configured — see that file.

## Generating a signed URL

```bash
pip install -r ../../scripts/requirements.txt
python ../../scripts/sign_cloudfront_url.py \
  --url "https://<cloudfront_domain_name>/motors" \
  --key-pair-id <cloudfront_key_pair_id> \
  --private-key cloudfront-signer.pem \
  --expires-in 3600
```

## What's deliberately not here

- **No custom domain / ACM cert.** The distribution ships on the default
  `*.cloudfront.net` domain. Add a Route 53 zone + `aws_acm_certificate`
  (in `us-east-1`, CloudFront requirement) and a `viewer_certificate`
  block if you want one.
- **No remote state backend.** Add an `s3` (+ `dynamodb` lock table)
  backend block in `versions.tf` before using this for anything you'd be
  upset to lose track of.
- **No live deploy.** Nobody has run `terraform apply` against a real AWS
  account from this repo yet — do that from your own credentials.
