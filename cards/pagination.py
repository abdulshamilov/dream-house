from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    Пагинация с поддержкой параметров:
    - page: номер страницы (по умолчанию 1)
    - limit: размер страницы (по умолчанию 10, максимум 100)
    """
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = 10
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page': self.page.number,
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
