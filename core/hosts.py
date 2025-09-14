from django_hosts import host, patterns

host_patterns = patterns(
    "",
    host(r"www\.localtest\.me", "core.urls", name="www"),
    host(r"localtest\.me", "core.urls", name="bare"),
    host(r"(?P<restaurant_name>.+)\.localtest\.me", "restaurants.urls", name="restaurant"),
)
