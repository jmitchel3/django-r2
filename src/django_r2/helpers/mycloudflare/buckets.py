import logging

from cloudflare.types.r2.bucket import Bucket as CloudflareBucket
from django.conf import settings

from .client import get_cloudflare_client
from .cors import default_cors

CLOUDFLARE_ACCOUNT_ID = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", None)

log = logging.getLogger(__name__)


def create_r2_bucket(bucket_name: str, location_hint: str = "auto") -> CloudflareBucket:
    client = get_cloudflare_client()
    try:
        r = client.r2.buckets.create(
            account_id=CLOUDFLARE_ACCOUNT_ID,
            location_hint=location_hint,
            name=bucket_name,
        )
        return r
    except Exception as e:
        log.error(e)
        return None


def update_r2_bucket_cors(bucket_name: str) -> bool:
    client = get_cloudflare_client()
    try:
        client.r2.buckets.cors.update(
            bucket_name=bucket_name,
            account_id=CLOUDFLARE_ACCOUNT_ID,
            rules=default_cors,
        )
        return True
    except Exception as e:
        log.error(e)
        return False


def delete_r2_bucket(bucket_name: str) -> bool:
    client = get_cloudflare_client()
    try:
        client.r2.buckets.delete(
            account_id=CLOUDFLARE_ACCOUNT_ID, bucket_name=bucket_name
        )
        return True
    except Exception as e:
        log.error(e)
        return False
