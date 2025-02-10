from cloudflare import Cloudflare
from django.conf import settings

CLOUDFLARE_API_KEY = getattr(settings, "CLOUDFLARE_API_KEY", None)
CLOUDFLARE_API_EMAIL = getattr(settings, "CLOUDFLARE_API_EMAIL", None)
CLOUDFLARE_BUCKET_MANAGER_TOKEN = getattr(
    settings, "CLOUDFLARE_BUCKET_MANAGER_TOKEN", None
)


def get_cloudflare_client() -> Cloudflare:
    return Cloudflare(
        api_email=CLOUDFLARE_API_EMAIL,
        api_key=CLOUDFLARE_API_KEY,
        api_token=CLOUDFLARE_BUCKET_MANAGER_TOKEN,
    )
