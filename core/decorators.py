import logging
from functools import wraps
from urllib.parse import urlparse

from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def get_client_ip(request):
    if x_forwarded_for := request.META.get("HTTP_X_FORWARDED_FOR"):
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown").strip()


def rate_limit(max_calls: int = 10, window: int = 60, key_func=get_client_ip):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view, request, *args, **kwargs):
            if settings.DEBUG:
                return view_func(view, request, *args, **kwargs)

            try:
                client_id = key_func(request)
                if not client_id or client_id == "unknown":
                    logger.warning("[RATE LIMIT] Could not determine a client identifier.")
                    return view_func(view, request, *args, **kwargs)

                path = urlparse(request.path).path.rstrip("/").lower()
                cache_key = f"rate_limit:{client_id}:{path}"

                request_count = cache.get(cache_key, 0)

                if request_count >= max_calls:
                    logger.warning(
                        f"[RATE LIMIT] Client '{client_id}' exceeded {max_calls} "
                        f"requests in {window}s for path '{path}'"
                    )
                    return Response(
                        {"detail": "Request limit exceeded."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                        headers={"Retry-After": str(window)},
                    )

                if request_count == 0:
                    cache.set(cache_key, 1, window)
                else:
                    cache.incr(cache_key)

            except Exception as e:
                logger.error(f"[RATE LIMIT] Cache access failed: {e}")

            return view_func(view, request, *args, **kwargs)

        return _wrapped_view

    return decorator
