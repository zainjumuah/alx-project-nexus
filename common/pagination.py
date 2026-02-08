from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    # I set a clear default so list endpoints don't dump too much at once.
    page_size = 10
    # I added this so `?page_size=...` actually works from Swagger/manual calls.
    page_size_query_param = "page_size"
    # I capped it so clients can tune page size without requesting huge payloads.
    max_page_size = 100
