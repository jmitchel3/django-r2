import logging
import time

from django.conf import settings

from . import client as myboto_client


def empty_bucket(bucket=None, s3_client=None, verbose=False, versions=False):
    logging.warning("This is dangerous, you have 10 seconds to reconsider.")
    logging.warning("This will delete all objects in the bucket.")
    logging.warning("Ctrl+C to cancel.")
    time.sleep(10)
    if s3_client is None:
        s3_client = myboto_client.s3_client
    if bucket is None:
        bucket = settings.AWS_STORAGE_BUCKET_NAME
    bucket = s3_client.Bucket(bucket)
    # Get the list of all objects in the bucket and delete each one

    if versions:
        try:
            versioned_bucket = s3_client.BucketVersioning(bucket)
            if versioned_bucket.status == "Enabled":
                versions = s3_client.Bucket(bucket).object_versions.all()
                for version in versions:
                    if verbose:
                        logging.info(
                            f"Deleting {version.object_key} "
                            f"version {version.version_id}"
                        )
                    version.delete()
                    if verbose:
                        logging.info(
                            f"{version.object_key} "
                            f"version {version.version_id} deleted"
                        )
        except Exception as e:
            logging.error(f"Error in deleting object versions: {e}")

    for obj in bucket.objects.all():
        if verbose:
            logging.info(f"Deleting {obj.key}")
        obj.delete()
        if verbose:
            logging.info(f"{obj.key} deleted")

    logging.info("All objects in the bucket have been deleted.")
