from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'perpage'
    # max_page_size = 5



class DefaultPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'perpage'
    # max_page_size = 5

    def get_paginated_response(self, data):
        if not data:
            if self.page.number > self.page.paginator.num_pages:
                return Response(
                    {
                        "detail": "Invalid page."
                    },
                    status=200
                )
            else:
                return Response(
                    {
                        "detail": "No results found",
                    },
                    status=200
                )
        else:
            return Response(
                {
                    "links": {
                        "next": self.get_next_link(),
                        "previous": self.get_previous_link(),
                    },
                    "total_objects": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "results": data,
                }
            )
#####
class UserPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'perpage'
    max_page_size = 5

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_objects": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
