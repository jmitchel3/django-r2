import logging
from functools import wraps

from django_r2 import settings

DJANGO_R2_USE_CELERY = getattr(settings, "DJANGO_R2_USE_CELERY", False)
DJANGO_R2_USE_DJANGO_QSTASH = getattr(settings, "DJANGO_R2_USE_DJANGO_QSTASH", False)

logger = logging.getLogger(__name__)


def proxy_task(task_function=None, **decorator_kwargs):
    """
    Decorator that makes Celery and django-qstash optional.
    If Celery or Django QStash is installed, the function can be
    wrapped as a celery task or django qstash task.
    If not, the function will be executed synchronously ignoring
    the decorator arguments.

    Args:
        task_function: The function to be decorated
        **celery_kwargs: Optional keyword arguments to pass to the Celery task decorator

    Returns:
        Either a celery task, a django-qstash task or the original function
        depending on celery and/or django-qstash, availability
    """

    def decorator(func):
        if not DJANGO_R2_USE_CELERY and not DJANGO_R2_USE_DJANGO_QSTASH:
            return func
        if DJANGO_R2_USE_DJANGO_QSTASH:
            try:
                from django_qstash import stashed_task

                @stashed_task(**decorator_kwargs)
                @wraps(func)
                def django_qstash_wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return django_qstash_wrapper
            except ImportError:
                logger.debug(
                    "Django QStash not installed, running function synchronously"
                )
                return func
        if DJANGO_R2_USE_CELERY:
            try:
                from celery import shared_task

                @shared_task(**decorator_kwargs)
                @wraps(func)
                def celery_wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return celery_wrapper

            except ImportError:
                logger.debug("Celery not installed, running function synchronously")
                return func

    if task_function is None:
        return decorator
    return decorator(task_function)
