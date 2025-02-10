import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import boto3
import helpers
from botocore.config import Config
from django.conf import settings

from django_r2.helpers.formatting import create_s3_filename

logger = logging.getLogger(__name__)


@dataclass
class MyS3Client:
    bucket: str = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
    access_key_id: str = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    secret_access_key: str = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    session_token: str = None
    region_name: str = "auto"
    endpoint_url: str = getattr(settings, "AWS_S3_ENDPOINT_URL", None)

    def __post_init__(self):
        if not all([self.access_key_id, self.secret_access_key, self.region_name]):
            USE_AWS_S3 = helpers.config("USE_AWS_S3", default=False)
            if USE_AWS_S3:
                logger.warning("AWS credentials are not set")
                return boto3.resource("s3")
        config = Config(signature_version="s3v4", retries={"max_attempts": 3})
        kwargs = {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region_name,
            "config": config,
        }
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        if self.session_token:
            kwargs["aws_session_token"] = self.session_token
        self.client = boto3.client("s3", **kwargs)

    def upload_fileobj(self, data, key):
        boto_s3_client = self.client
        return boto_s3_client.upload_fileobj(
            data,
            self.bucket,
            key,
        )

    def get_presigned_upload_url(self, key, expires_in=3600):
        return self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_presigned_download_url(
        self,
        key: str,
        filename: Optional[str] = None,
        expires_in=3600,
        force_download: bool = False,
    ):
        client = self.client
        if isinstance(key, Path):
            key = str(key)

        params = {
            "Bucket": self.bucket,
            "Key": key,
        }

        if filename:
            # create a URL-safe file name from the input string (if any)
            filename = create_s3_filename(filename, object_id=None)
            encoded_filename = quote(filename)
            disposition = "attachment" if force_download else "inline"
            params["ResponseContentDisposition"] = (
                f"{disposition}; filename*=UTF-8''{encoded_filename}"
            )
        elif force_download:
            params["ResponseContentDisposition"] = "attachment"
        presigned_url = client.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires_in,
        )
        return presigned_url


def get_s3_temp_client(access_key_id=None, secret_access_key=None, session_token=None):
    AWS_S3_ENDPOINT_URL = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    config = Config(signature_version="s3v4", retries={"max_attempts": 3})
    kwargs = {
        "aws_access_key_id": access_key_id,
        "aws_secret_access_key": secret_access_key,
        "region_name": "auto",
        "config": config,
    }
    if AWS_S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = AWS_S3_ENDPOINT_URL
    if session_token:
        kwargs["aws_session_token"] = session_token
    return boto3.client("s3", **kwargs)


@lru_cache
def get_s3_client():
    AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    AWS_S3_REGION_NAME = getattr(settings, "AWS_S3_REGION_NAME", None)
    AWS_S3_ENDPOINT_URL = getattr(settings, "AWS_S3_ENDPOINT_URL", None)

    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME]):
        USE_AWS_S3 = helpers.config("USE_AWS_S3", default=False)
        if USE_AWS_S3:
            logger.warning("AWS credentials are not set")
            return boto3.resource("s3")

    # Configure boto3 to use SigV4
    config = Config(signature_version="s3v4", retries={"max_attempts": 3})

    kwargs = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_S3_REGION_NAME,
        "config": config,  # Add the config here
    }
    if AWS_S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = AWS_S3_ENDPOINT_URL
    return boto3.client("s3", **kwargs)


@lru_cache
def get_s3_resource():
    AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY", None)
    AWS_S3_REGION_NAME = getattr(settings, "AWS_S3_REGION_NAME", None)
    AWS_S3_ENDPOINT_URL = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME]):
        USE_AWS_S3 = helpers.config("USE_AWS_S3", default=False)
        if USE_AWS_S3:
            logger.warning("AWS credentials are not set")
            return boto3.resource("s3")
    kwargs = {
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
        "region_name": AWS_S3_REGION_NAME,
    }
    if AWS_S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = AWS_S3_ENDPOINT_URL
    return boto3.resource("s3", **kwargs)


s3_client = get_s3_client()
s3_resource = get_s3_resource()
