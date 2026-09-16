#!/usr/bin/env python3
"""Mint a CloudFront signed URL or signed cookies for the f1-api distribution.

The distribution's default cache behavior has a trusted key group
(terraform/aws/cloudfront.tf), so CloudFront rejects any request that
doesn't carry a valid signature from the matching private key. This script
is the operator-side tool that creates those signatures — it never runs
inside the app itself.

Examples:

    # One URL, valid for an hour, restricted to that exact path
    python sign_cloudfront_url.py \\
        --url https://d123abc.cloudfront.net/motors \\
        --key-pair-id K2JXXXXXXXX \\
        --private-key cloudfront-signer.pem

    # Signed cookies valid across every path on the distribution, for use
    # with any client (curl, browser, requests session) that sends cookies
    python sign_cloudfront_url.py \\
        --url https://d123abc.cloudfront.net/ \\
        --key-pair-id K2JXXXXXXXX \\
        --private-key cloudfront-signer.pem \\
        --cookies --wildcard
"""
import argparse
import base64
import json
import time
from urllib.parse import urlsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def cloudfront_b64encode(data: bytes) -> str:
    # CloudFront's flavor of base64: standard base64, then swap the three
    # characters that aren't URL/cookie-safe.
    encoded = base64.b64encode(data).decode("ascii")
    return encoded.replace("+", "-").replace("=", "_").replace("/", "~")


def build_policy(resource: str, expires_at: int) -> bytes:
    policy = {
        "Statement": [
            {
                "Resource": resource,
                "Condition": {"DateLessThan": {"AWS:EpochTime": expires_at}},
            }
        ]
    }
    # No whitespace: CloudFront verifies the signature over these exact bytes.
    return json.dumps(policy, separators=(",", ":")).encode("utf-8")


def sign_policy(policy_bytes: bytes, private_key) -> bytes:
    return private_key.sign(policy_bytes, padding.PKCS1v15(), hashes.SHA1())


def load_private_key(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", required=True, help="URL to sign (or, with --wildcard, the URL whose scheme+host is used)")
    parser.add_argument("--key-pair-id", required=True, help="CloudFront public key ID (terraform output cloudfront_key_pair_id)")
    parser.add_argument("--private-key", required=True, help="Path to the PEM private key matching that public key")
    parser.add_argument("--expires-in", type=int, default=3600, help="Seconds from now until the signature expires (default: 3600)")
    parser.add_argument("--wildcard", action="store_true", help="Sign scheme://host/* instead of the exact URL, so it covers every path")
    parser.add_argument("--cookies", action="store_true", help="Print Set-Cookie-style signed cookie values instead of a signed URL")
    args = parser.parse_args()

    expires_at = int(time.time()) + args.expires_in
    parts = urlsplit(args.url)

    resource = f"{parts.scheme}://{parts.netloc}/*" if args.wildcard else args.url

    private_key = load_private_key(args.private_key)
    policy_bytes = build_policy(resource, expires_at)
    signature = sign_policy(policy_bytes, private_key)

    encoded_policy = cloudfront_b64encode(policy_bytes)
    encoded_signature = cloudfront_b64encode(signature)

    if args.cookies:
        print(f"CloudFront-Policy={encoded_policy}")
        print(f"CloudFront-Signature={encoded_signature}")
        print(f"CloudFront-Key-Pair-Id={args.key_pair_id}")
        print()
        print("Example:")
        cookie_flags = "Domain=" + parts.netloc + "; Path=/; Secure; HttpOnly"
        print(f'curl --cookie "CloudFront-Policy={encoded_policy}; CloudFront-Signature={encoded_signature}; CloudFront-Key-Pair-Id={args.key_pair_id}" "{args.url}"')
        print(f"# ({cookie_flags} when setting these in a browser)")
    else:
        separator = "&" if "?" in args.url else "?"
        signed_url = f"{args.url}{separator}Policy={encoded_policy}&Signature={encoded_signature}&Key-Pair-Id={args.key_pair_id}"
        print(signed_url)


if __name__ == "__main__":
    main()
