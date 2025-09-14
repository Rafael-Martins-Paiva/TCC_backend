class HostDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"HostDebugMiddleware: HTTP_HOST = {request.META.get('HTTP_HOST')}")
        print(f"HostDebugMiddleware: request.host = {getattr(request, 'host', 'N/A')}")
        print(f"HostDebugMiddleware: request.urlconf = {getattr(request, 'urlconf', 'N/A')}")
        print(
            f"HostDebugMiddleware: request.resolver_match.kwargs = {getattr(request.resolver_match, 'kwargs', 'N/A')}"
        )
        response = self.get_response(request)
        return response
