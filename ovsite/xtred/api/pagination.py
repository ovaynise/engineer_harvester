
from rest_framework.pagination import PageNumberPagination


class ConstructionPagination(PageNumberPagination):
    page_size = 10