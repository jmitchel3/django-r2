from __future__ import annotations

import warnings

from django.conf import settings

CLOUDFLARE_ACCESS_KEY = getattr(settings, "CLOUDFLARE_ACCESS_KEY", None)
CLOUDFLARE_SECRET_KEY = getattr(settings, "CLOUDFLARE_SECRET_KEY", None)
CLOUDFLARE_ACCOUNT_ID = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", None)


DJANGO_R2_BASE_PATH = getattr(settings, "DJANGO_R2_BASE_PATH", "/buckets")
DJANGO_R2_USE_CELERY = getattr(settings, "DJANGO_R2_USE_CELERY", False)
DJANGO_R2_USE_DJANGO_QSTASH = getattr(settings, "DJANGO_R2_USE_DJANGO_QSTASH", False)

if not all([CLOUDFLARE_ACCESS_KEY, CLOUDFLARE_SECRET_KEY]):
    warnings.warn(
        """DJANGO_SETTINGS_MODULE (settings.py required)
        requires CLOUDFLARE_ACCESS_KEY and CLOUDFLARE_SECRET_KEY 
        should be set for R2 functionality""",
        RuntimeWarning,
        stacklevel=2,
    )
