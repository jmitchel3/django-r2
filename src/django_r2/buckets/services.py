import uuid

from django.utils import timezone

from django_r2.helpers.mycloudflare.client import get_cloudflare_client
from django_r2.models import Bucket, BucketCredentials


def get_today_bucket_credentials_by_bucket_id(bucket_id: uuid.UUID | str):
    bucket = Bucket.objects.get(id=bucket_id)
    qs = BucketCredentials.objects.filter(bucket=bucket, expires_at__gte=timezone.now())
    if qs.exists():
        cred_obj = qs.first()
        return cred_obj
    cred_obj = BucketCredentials.objects.create(
        bucket=bucket,
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    cloudflare_client = get_cloudflare_client()
    request_data = {
        "bucket": bucket.name,
        "account_id": cred_obj.account_id,
        "parent_access_key_id": cred_obj.parent_access_key_id,
        "ttl_seconds": cred_obj.ttl_seconds,
        "permission": cred_obj.permission,
    }
    cred_response = cloudflare_client.r2.temporary_credentials.create(**request_data)
    cred_obj.access_key_id = cred_response.access_key_id
    cred_obj.secret_access_key = cred_response.secret_access_key
    cred_obj.session_token = cred_response.session_token
    cred_obj.save()
    return cred_obj
