from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views import View


class BucketListView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponse("Use the Django Admin to manage buckets")
