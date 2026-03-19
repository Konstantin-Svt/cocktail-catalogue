import uuid

from django.conf import settings


class AnonymousUserCookieMiddleware:
    COOKIE_NAME = "anon_id"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        anon_id = request.COOKIES.get(self.COOKIE_NAME)
        cookie_absent = False
        if not anon_id:
            anon_id = str(uuid.uuid4())
            cookie_absent = True
        request.anon_id = anon_id

        response = self.get_response(request)
        if cookie_absent:
            response.set_cookie(
                self.COOKIE_NAME,
                anon_id,
                max_age=31536000,
                secure=not settings.DEBUG,
                samesite="Lax" if settings.DEBUG else "None",
                httponly=False
            )
        return response
