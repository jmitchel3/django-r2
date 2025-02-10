from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.core import signing
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from django_r2.helpers.packages import myboto
from django_r2.services import buckets as buckets_services
from django_r2.services import objects as objects_services


@login_required
def upload_view(request, id=None):
    """
    Renders the file upload field
    Using JavaScript, user initiates upload
    View responds with s3-signed url for direct upload
    JavaScript uploads direct to s3
    """
    project_id = request.namespace.id
    bucket_credentials = buckets_services.get_credentials_from_request(request)
    if bucket_credentials is None:
        return HttpResponseBadRequest(
            "There's an error with uploading files to your account."
        )
    template_name = "upload/upload_view.html"
    if request.htmx:
        template_name = "upload/snippets/upload.html"
    if request.method == "POST":
        filename = request.POST.get("filename")
        if not filename:
            return JsonResponse({"error": "Filename is required"}, status=400)
        name = myboto.formatting.create_s3_filename(filename)
        if name is None:
            return JsonResponse({"error": "Invalid filename"}, status=400)
        instance = objects_services.preflight_object_create(
            project_id, filename, request.user
        )
        key = instance.get_s3_key()
        url = bucket_credentials.presign_upload_url(
            key=key, expires_in=60 * 60 * 24 * 7
        )
        object_data = {
            "object_id": str(instance.id),
            "project_id": str(project_id),
            "key": str(key),
            "filename": str(instance.keyname),
        }
        object_data_signed = signing.dumps(object_data, salt="object-upload")
        return JsonResponse(
            {
                "url": url,
                "filename": instance.keyname,
                "object_data": object_data_signed,
                "key": key,
            }
        )
    return render(request, template_name, {})


@login_required
@require_POST
def upload_complete_view(request):
    completed = False
    request_data = {}
    try:
        request_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    completed = request_data.get("completed", False)
    object_data_raw = request_data.get("object_data")
    try:
        object_data = signing.loads(object_data_raw, salt="object-upload")
    except signing.BadSignature:
        object_data = None

    if not object_data:
        msg = "Signed object data is required"
        return JsonResponse({"error": msg}, status=400)
    file_data = request_data.get("file_data")
    instance = objects_services.postflight_object_update(
        object_data, uploaded=completed, file_data=file_data
    )
    url = instance.get_absolute_url()
    request.session["refresh_objects_cache"] = True
    return JsonResponse({"status": "ok", "url": url})
