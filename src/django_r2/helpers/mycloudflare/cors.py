from django.conf import settings

default_cors = [
    {
        "allowed": {
            "origins": [
                f"https://{settings.PARENT_SUBDOMAIN}.{settings.PARENT_HOST}",
                f"https://{settings.PARENT_HOST}",
                f"http://{settings.PARENT_SUBDOMAIN}.{settings.PARENT_HOST}",
                f"http://{settings.PARENT_HOST}",
            ],
            "methods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
            "headers": [
                "Content-Type",
                "Origin",
                "x-amz-acl",
                "x-amz-content-sha256",
                "x-amz-date",
            ],
        },
        "exposeHeaders": ["ETag"],
        "maxAgeSeconds": 3600,
    }
]
