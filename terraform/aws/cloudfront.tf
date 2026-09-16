resource "aws_cloudfront_public_key" "signer" {
  name        = "${var.project_name}-signer"
  encoded_key = var.cloudfront_public_key_pem
  comment     = "Verifies signed URLs/cookies minted by scripts/sign_cloudfront_url.py"
}

resource "aws_cloudfront_key_group" "signer" {
  name    = "${var.project_name}-signer"
  comment = "Trusted key group for ${var.project_name}"
  items   = [aws_cloudfront_public_key.signer.id]
}

# Managed policy: forward every header/cookie/query string except Host to
# the origin. An API needs its full request forwarded (auth headers,
# query params, all HTTP methods) unlike a typical static-asset
# distribution, so none of the "CORS" or "AllViewer" managed policies that
# drop things are a fit.
data "aws_cloudfront_origin_request_policy" "all_viewer_except_host" {
  name = "Managed-AllViewerExceptHostHeader"
}

# Managed policy: don't cache anything. This is a dynamic API, not a CDN
# for static assets — caching is left to the app/client, not CloudFront.
data "aws_cloudfront_cache_policy" "caching_disabled" {
  name = "Managed-CachingDisabled"
}

resource "aws_cloudfront_distribution" "this" {
  enabled     = true
  comment     = var.project_name
  price_class = var.cloudfront_price_class

  origin {
    domain_name = aws_lb.this.dns_name
    origin_id   = "alb"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = "X-Origin-Verify"
      value = random_password.origin_verify.result
    }
  }

  default_cache_behavior {
    target_origin_id       = "alb"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]

    cache_policy_id          = data.aws_cloudfront_cache_policy.caching_disabled.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.all_viewer_except_host.id

    # This is the actual access control: without a valid signed URL or
    # signed cookie from the key pair in aws_cloudfront_key_group.signer,
    # CloudFront returns 403 before the request ever reaches the ALB.
    trusted_key_groups = [aws_cloudfront_key_group.signer.id]
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # No custom domain wired up here — this ships on the default
  # *.cloudfront.net domain and its default certificate. Bring your own
  # domain + ACM cert (in us-east-1) and set viewer_certificate
  # accordingly if that's needed later.
  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = local.common_tags
}
