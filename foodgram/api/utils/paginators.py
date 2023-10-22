from rest_framework import pagination

from recipes.constants import PAGE_SIZE_QUERY_PARAM, PAGE_SIZE


class CustomPaginator(pagination.PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
