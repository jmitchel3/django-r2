import mimetypes
import tempfile
from pathlib import Path

import requests
from buckets import services as buckets_services
from django.apps import apps
from django.db import transaction
from helpers.packages import myboto
from objects import services as objects_services

from django_r2.decorators import proxy_task


@proxy_task
def process_url_upload_task(upload_request_id):
    """
    Downloads file from URL and uploads it to S3
    Updates URLUploadRequest status throughout the process
    """
    with transaction.atomic():
        URLUploadRequest = apps.get_model("uploads", "URLUploadRequest")
        upload_request = URLUploadRequest.objects.get(id=upload_request_id)
        if upload_request.completed:
            return "Upload request already completed"
        # Increment try count
        upload_request.tries += 1
        URLUploadRequest.objects.filter(id=upload_request_id).update(
            tries=upload_request.tries
        )

        # Get filename from URL
        url_path = requests.utils.urlparse(upload_request.url).path
        filename = Path(url_path).name or "downloaded_file"

        # Create temporary file
        with tempfile.NamedTemporaryFile() as tmp_file:
            # Download file
            response = requests.get(upload_request.url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Prepare S3 upload
            name = myboto.formatting.create_s3_filename(filename)
            if name is None:
                raise ValueError("Invalid filename")

            # Create object instance
            instance = objects_services.preflight_object_create(
                upload_request.project_id, filename, upload_request.added_by
            )

            # Get bucket credentials
            bucket_credentials = (
                buckets_services.get_today_bucket_credentials_by_project_id(
                    upload_request.project_id
                )
            )
            if not bucket_credentials:
                raise ValueError("No bucket credentials available")

            # Upload to S3
            key = instance.get_s3_key()
            my_s3_client = bucket_credentials.get_my_s3_client()
            boto_s3_client = my_s3_client.client

            file_size = 0
            with open(tmp_file.name, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    file_size += len(chunk)
                    f.write(chunk)

            boto_s3_client.upload_fileobj(
                tmp_file,
                bucket_credentials.bucket.name,
                key,
            )

            file_data = {
                "size": file_size,
                "type": mimetypes.guess_type(filename)[0],
                "duration": None,
                "width": None,
                "height": None,
            }

            # Update object status
            object_data = {
                "object_id": str(instance.id),
                "project_id": str(upload_request.project_id),
                "key": str(key),
                "filename": str(instance.keyname),
            }

            # Mark upload as complete
            objects_services.postflight_object_update(
                object_data,
                uploaded=True,
                file_data=file_data,  # Add file metadata if needed
            )

            # Update upload request
            upload_request.completed = True
            upload_request.object = instance
            URLUploadRequest.objects.filter(id=upload_request_id).update(
                completed=True,
                object=instance,
            )

            return f"Successfully uploaded file from {upload_request.url}"
