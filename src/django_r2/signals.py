import hashlib

from cloudflare.types.r2.bucket import Bucket as CloudflareBucket
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from helpers.packages.mycloudflare.buckets import (
    create_r2_bucket,
    delete_r2_bucket,
    update_r2_bucket_cors,
)
from projects.models import Project

from .models import Bucket


@receiver(post_save, sender=Project)
def project_post_save_receiver(sender, instance, **kwargs):
    bucket_obj, bucket_created = Bucket.objects.get_or_create(project=instance)
    if not bucket_obj.active_in_cloudflare:
        # Create a hash using the project's UUID (which never changes)
        hash_input = str(instance.id).encode("utf-8")
        hash_object = hashlib.sha256(hash_input)
        # Take first 16 characters of the hex digest (64 bits)
        hash_prefix = hash_object.hexdigest()[:16]
        bucket_prefix = "srv" if not settings.DEBUG else "srv-dev"
        bucket_name = f"{bucket_prefix}-{hash_prefix}"
        cf_bucket_response = create_r2_bucket(bucket_name)
        cors_response = update_r2_bucket_cors(bucket_name)
        if isinstance(cf_bucket_response, CloudflareBucket) and cors_response:
            bucket_obj.name = cf_bucket_response.name
            bucket_obj.active_in_cloudflare = True
            bucket_obj.active_in_cloudflare_at = timezone.now()
            bucket_obj.save()
            qs = Project.objects.filter(id=instance.id)
            qs.update(bucket_name=bucket_name, bucket_active=True)


@receiver(post_delete, sender=Bucket)
def bucket_post_delete_receiver(sender, instance, **kwargs):
    delete_r2_bucket(instance.name)
