from __future__ import annotations

import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, View

from django_r2.models import Object
from django_r2.services import buckets as buckets_services
from django_r2.services import objects as objects_services


class ObjectListView(LoginRequiredMixin, ListView):
    """
    List of objects for a project based on the namespace selected
    """

    template_name = "objects/list.html"
    paginate_by = 50

    def get_queryset(self):
        request = self.request
        bucket_id = self.kwargs.get("bucket_id")

        # Track refresh timestamps
        refresh_history = request.session.get("objects_refresh_history", [])
        current_time = time.time()

        # Remove timestamps older than 10 seconds
        refresh_history = [t for t in refresh_history if current_time - t <= 10]
        refresh_history.append(current_time)
        request.session["objects_refresh_history"] = refresh_history

        # Set refresh_cache to True if there are 3 or more refreshes within 10 seconds
        refresh_cache = request.session.get("refresh_objects_cache", False)
        if len(refresh_history) >= 3:
            refresh_cache = True
            refresh_history.clear()
            request.session["objects_refresh_history"] = refresh_history

        qs = objects_services.get_paginated_objects_for_bucket(
            bucket_id,
            page=self.request.GET.get("page", 1),
            page_size=self.paginate_by,
            refresh_cache=refresh_cache,
        )
        if refresh_cache:
            try:
                del self.request.session["refresh_objects_cache"]
            except KeyError:
                pass
        return qs


class ObjectDetailView(LoginRequiredMixin, DetailView):
    model = Object
    template_name = "objects/detail.html"

    def get_object(self, queryset=None):
        bucket_id = self.kwargs.get("bucket_id")
        object_id = self.kwargs.get("pk")
        return objects_services.get_object_by_id(object_id, bucket_id)


class ObjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Object
    template_name = "objects/confirm_delete.html"
    success_message = "File deleted successfully"
    success_url = reverse_lazy("objects:list")

    def get_object(self, queryset=None):
        object_id = self.kwargs.get("pk")
        return objects_services.get_object_by_id(object_id)

    def get_success_url(self):
        self.request.session["refresh_objects_cache"] = True
        return reverse_lazy("objects:list")


class ObjectProxyDownloadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        object_id = kwargs.get("pk")
        project_id = request.namespace.id
        bucket_credentials = buckets_services.get_credentials_from_request(request)
        if bucket_credentials is None:
            return HttpResponseBadRequest(
                "There's an error with uploading files to your account."
            )
        instance = objects_services.get_object_by_id(object_id, project_id)
        fname = instance.keyname
        s3_key = instance.get_s3_key()
        download_url = bucket_credentials.presign_download_url(
            key=s3_key, filename=fname, force_download=True
        )
        response = redirect(download_url)
        # Add headers to encourage download behavior
        # response['Content-Type'] = 'application/octet-stream'
        response["Content-Disposition"] = f'inline; filename="{fname}"'
        return response
