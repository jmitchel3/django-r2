import pathlib
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.
from django_r2.buckets import services as buckets_services
from django_r2.helpers.formatting.filenames import create_s3_filename
from django_r2.helpers.formatting.humanize import humanize_filesize
from django_r2.models import Bucket

User = settings.AUTH_USER_MODEL


class Object(models.Model):
    """
    A file uploaded to the system.
    """

    class SourceChoices(models.TextChoices):
        USER = "user", "User"
        BOT = "bot", "Bot"

    id = models.UUIDField(
        default=uuid.uuid1, editable=False, unique=True, primary_key=True
    )
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    source = models.CharField(
        max_length=10,
        choices=SourceChoices.choices,
        default=SourceChoices.USER,
    )
    keyname = models.CharField(
        max_length=255,
        help_text="auto-formatted s3 filename",
        db_index=True,
        blank=True,
        null=True,
    )
    downloadable_filename = models.CharField(
        max_length=255,
        help_text="Downloadable filename",
        blank=True,
        null=True,
    )
    filename = models.CharField(
        max_length=255,
        help_text="Uploaded file name",
        db_index=True,
        null=True,
    )
    file_extension = models.CharField(
        max_length=20,
        help_text="Uploaded file extension",
        blank=True,
        null=True,
    )
    uploaded_width = models.IntegerField(
        help_text="Uploaded file width in pixels",
        blank=True,
        null=True,
    )
    uploaded_height = models.IntegerField(
        help_text="Uploaded file height in pixels",
        blank=True,
        null=True,
    )
    uploaded_size = models.IntegerField(
        help_text="Uploaded file size in bytes",
        blank=True,
        null=True,
    )
    display_size = models.CharField(
        max_length=255,
        help_text="Uploaded file size in human readable format",
        blank=True,
        null=True,
    )
    uploaded_type = models.CharField(
        max_length=255,
        help_text="Uploaded file type",
        blank=True,
        null=True,
    )
    is_image_file = models.BooleanField(default=False)
    is_video_file = models.BooleanField(default=False)
    is_audio_file = models.BooleanField(default=False)
    uploaded_metadata = models.JSONField(
        help_text="Uploaded file metadata",
        blank=True,
        null=True,
    )
    uploaded_duration = models.DecimalField(
        help_text="Uploaded file duration in seconds with microsecond precision",
        max_digits=12,
        decimal_places=6,
        blank=True,
        null=True,
    )
    uploaded = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(
        help_text="Date and time the file was successfully uploaded to S3",
        auto_now_add=False,
        auto_now=False,
        blank=True,
        null=True,
    )
    errors = models.JSONField(default=dict, blank=True, null=True)
    errors_at = models.DateTimeField(
        help_text="Date and time the file upload failed",
        auto_now_add=False,
        auto_now=False,
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("objects:detail", kwargs={"pk": self.id})

    def get_proxy_download_url(self):
        return reverse("objects:download", kwargs={"pk": self.id})

    def get_s3_download_url(self, force_download=False) -> str | None:
        s3_key = self.get_s3_key()
        if not s3_key:
            return None
        uploaded_filename = self.filename
        file_ext = self.file_extension
        fname = f"{uploaded_filename}.{file_ext}"
        bucket_credentials = buckets_services.get_today_bucket_credentials_by_bucket_id(
            self.bucket.id
        )
        return bucket_credentials.presign_download_url(
            s3_key,
            filename=fname,
            force_download=force_download,
        )

    def save(self, *args, **kwargs):
        if self.filename:
            if not self.keyname:
                """
                Set a unique keyname for the object and
                today's upload.
                """
                self.keyname = create_s3_filename(
                    self.filename, object_id=self.id, id_max_length=5
                )
            if not self.file_extension:
                self.file_extension = pathlib.Path(self.filename).suffix
            if not self.downloadable_filename:
                fname_stem = pathlib.Path(self.filename).stem
                self.downloadable_filename = create_s3_filename(
                    f"{fname_stem}.{self.file_extension}", object_id=self.id
                )
        if self.uploaded and not self.uploaded_at:
            self.uploaded_at = timezone.now()
        if self.errors and not self.errors_at:
            self.errors_at = timezone.now()

        # Update file type booleans
        if self.uploaded_type:
            self.is_image_file = self.uploaded_type.startswith("image/")
            self.is_video_file = self.uploaded_type.startswith("video/")
            self.is_audio_file = self.uploaded_type.startswith("audio/")
        if self.uploaded_size and not self.display_size:
            self.display_size = humanize_filesize(self.uploaded_size)
        if self.downloadable_filename and self.filename:
            self.downloadable_filename = self.downloadable_filename
        super().save(*args, **kwargs)

    def date_folders(self):
        return f"{self.created_at.year}/{self.created_at.month}/{self.created_at.day}/"

    def get_prefix(self):
        folder_path = self.date_folders().rstrip("/")
        return f"{folder_path}/"

    def get_s3_key(self):
        prefix = self.get_prefix().rstrip("/")
        return f"{prefix}/{self.keyname}"

    def get_user_filename(self, strip_extension=False):
        if strip_extension:
            return pathlib.Path(self.filename).stem
        return self.filename

    @property
    def uuid(self):
        return self.id

    @property
    def type(self) -> str:
        if not self.uploaded_type:
            return ""
        return self.uploaded_type
