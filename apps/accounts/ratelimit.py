from functools import wraps

from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect


def ratelimit(key, limit=5, period=300):
    """Rate limit POST requests by IP address.

    Args:
        key: Cache key prefix for this endpoint.
        limit: Max POST attempts allowed within period (default: 5).
        period: Time window in seconds (default: 300 = 5 minutes).
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == "POST":
                ip = request.META.get("REMOTE_ADDR", "")
                cache_key = f"rl:{key}:{ip}"
                attempts = cache.get(cache_key, 0)
                if attempts >= limit:
                    messages.error(request, "Too many attempts. Please try again later.")
                    return redirect(request.path)
                cache.set(cache_key, attempts + 1, period)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
