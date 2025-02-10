from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from django_r2 import settings
from django_r2.models import (
    Bucket,
    BucketCredentials,
    Object,
)


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ("name", "cloudflare_link")
    search_fields = ("name",)

    readonly_fields = (
        "name",
        "cloudflare_link",
        "location_hint",
        "storage_class",
        "active_in_cloudflare",
        "active_in_cloudflare_at",
    )

    def cloudflare_link(self, obj):
        CLOUDFLARE_ACCOUNT_ID = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", None)
        if obj and obj.pk:
            url = f"https://dash.cloudflare.com/{CLOUDFLARE_ACCOUNT_ID}/r2/default/buckets/{obj.name}"
            return format_html(
                '<a target="_blank" href="{}">Open in Cloudflare</a>', url
            )
        return "-"

    cloudflare_link.short_description = "Cloudflare"


admin.site.register(BucketCredentials)


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ("filename", "bucket", "uploaded", "uploaded_at")
    list_filter = ("uploaded",)
    readonly_fields = (
        "uploaded_size",
        "uploaded_type",
        "uploaded_metadata",
        "uploaded_duration",
        "uploaded_width",
        "uploaded_height",
        "uploaded_at",
        "uploaded",
        "errors",
        "errors_at",
        "added_by",
        "created_at",
        "updated_at",
        "keyname",
        "type",
        "download_buttons",
    )
    search_fields = ("filename",)
    ordering = ("-uploaded_at",)
    fieldsets = (
        (
            "File Information",
            {
                "fields": (
                    "filename",
                    "keyname",
                    "bucket",
                    "added_by",
                    "type",
                    "uploaded_at",
                    "download_buttons",
                )
            },
        ),
        (
            "Upload Details",
            {
                "fields": (
                    "uploaded",
                    "uploaded_size",
                    "uploaded_type",
                    "uploaded_duration",
                    "uploaded_width",
                    "uploaded_height",
                    "uploaded_metadata",
                )
            },
        ),
        (
            "Error Information",
            {
                "fields": (
                    "errors",
                    "errors_at",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description="Download")
    def download_buttons(self, obj):
        url = obj.get_s3_download_url()
        s3_button = f'<a href="{url}" target="_blank">Download from S3</a>'
        s3_button2 = f'<a href="{url}" target="_blank">Download</a>'
        html_ = "<br/>".join([s3_button, s3_button2])
        return mark_safe(html_)
