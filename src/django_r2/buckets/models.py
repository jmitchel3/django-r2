import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models

from django_r2.helpers import myboto

OWNER_MODEL = settings.AUTH_USER_MODEL


CLOUDFLARE_ACCOUNT_ID = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", None)
CLOUDFLARE_BUCKET_MANAGER_ACCESS_KEY = getattr(
    settings, "CLOUDFLARE_BUCKET_MANAGER_ACCESS_KEY", None
)


class Bucket(models.Model):
    """
    One bucket per project.
    """

    class StorageClass(models.TextChoices):
        STANDARD = "Standard", "Standard"
        INFREQUENT_ACCESS = "InfrequentAccess", "Infrequent Access"

    class LocationHint(models.TextChoices):
        APAC = "apac", "Asia Pacific"
        E_EUR = "eeur", "Europe"
        E_NAM = "enam", "North America"
        W_EUR = "weur", "Western Europe"
        W_NAM = "wnam", "Western North America"
        AUTO = "auto", "Auto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        OWNER_MODEL, on_delete=models.CASCADE, related_name="buckets"
    )
    name = models.CharField(max_length=64, blank=True, null=True)
    storage_class = models.CharField(
        max_length=20, choices=StorageClass.choices, default=StorageClass.STANDARD
    )
    location_hint = models.CharField(
        max_length=5, choices=LocationHint.choices, default=LocationHint.AUTO
    )
    active_in_cloudflare = models.BooleanField(default=False)
    active_in_cloudflare_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def one_day_ttl():
    return 60 * 60 * 24


class BucketCredentials(models.Model):
    class Permission(models.TextChoices):
        READ_WRITE = "object-read-write", "Object Read Write"
        READ_ONLY = "object-read", "Object Read Only"

    bucket = models.OneToOneField(Bucket, on_delete=models.CASCADE)
    access_key_id = models.TextField(blank=True, null=True)
    secret_access_key = models.TextField(blank=True, null=True)
    session_token = models.TextField(blank=True, null=True)
    account_id = models.CharField(
        max_length=120, null=True, default=CLOUDFLARE_ACCOUNT_ID
    )
    parent_access_key_id = models.CharField(
        max_length=240, null=True, default=CLOUDFLARE_BUCKET_MANAGER_ACCESS_KEY
    )
    ttl_seconds = models.IntegerField(default=one_day_ttl)
    expires_at = models.DateTimeField(null=True, blank=True)
    permission = models.CharField(
        max_length=64, choices=Permission.choices, default=Permission.READ_WRITE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.project and self.bucket:
            self.project = self.bucket.project or None
        if self.created_at and not self.expires_at:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
        super().save(*args, **kwargs)

    def get_access_data(self):
        return {
            "bucket": self.bucket,
            "access_key_id": self.access_key_id,
            "secret_access_key": self.secret_access_key,
            "session_token": self.session_token,
        }

    class Meta:
        verbose_name = "Bucket Credentials"
        verbose_name_plural = "Bucket Credentials"
        ordering = ["-created_at"]

    def get_my_s3_client(self):
        return myboto.client.MyS3Client(
            bucket=self.bucket.name,
            access_key_id=self.access_key_id,
            secret_access_key=self.secret_access_key,
            session_token=self.session_token,
        )

    def get_s3_client(self):
        return self.get_my_s3_client().client

    def presign_upload_url(self, key, expires_in=60 * 60 * 24 * 7):
        my_s3_client = self.get_my_s3_client()
        url = my_s3_client.get_presigned_upload_url(key=key, expires_in=expires_in)
        return url

    def presign_download_url(
        self, key, filename=None, force_download=False, expires_in=60 * 60 * 24 * 7
    ):
        my_s3_client = self.get_my_s3_client()
        url = my_s3_client.get_presigned_download_url(
            key=key,
            filename=filename,
            expires_in=expires_in,
            force_download=force_download,
        )
        return url

    def delete_object(self, key):
        s3_client = self.get_s3_client()
        return s3_client.delete_object(Bucket=self.bucket.name, Key=key)
