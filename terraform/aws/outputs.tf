output "ecr_repository_url" {
  description = "Push images here (also used by the deploy workflow)"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "alb_dns_name" {
  description = "Only reachable from CloudFront's IP ranges (see security_groups.tf) — not a useful URL to visit directly"
  value       = aws_lb.this.dns_name
}

output "cloudfront_domain_name" {
  description = "The public entrypoint. Every request needs a valid signed URL/cookie — see scripts/sign_cloudfront_url.py"
  value       = aws_cloudfront_distribution.this.domain_name
}

output "cloudfront_key_pair_id" {
  description = "Pass this as --key-pair-id to scripts/sign_cloudfront_url.py"
  value       = aws_cloudfront_public_key.signer.id
}

output "rds_endpoint" {
  value     = aws_db_instance.this.address
  sensitive = true
}
