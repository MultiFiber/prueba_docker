from rest_framework import pagination
from rest_framework.response import Response


class LinkHeaderPagination(pagination.PageNumberPagination):
    "http://www.django-rest-framework.org/api-guide/pagination/#header-based-pagination"

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        go_next = None
        go_prev = None

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
            go_next = self.page.next_page_number()
            go_prev = self.page.previous_page_number()
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
            go_next = self.page.next_page_number()
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'
            go_prev = self.page.previous_page_number()
        else:
            link = ''

        link = link.format(next_url=next_url, previous_url=previous_url)
        headers = {'Link': link} if link else {}
        if go_next or go_prev:
            headers['go_prev'] = go_prev if go_prev else 0
            headers['go_next'] = go_next if go_next else 0

        return Response(data, headers=headers)



class DefaultResultsSetPagination(LinkHeaderPagination):
    page_size = 100


class LargeResultsSetPagination(LinkHeaderPagination):
    page_size = 1000


class VerySmallResultsSetPagination(LinkHeaderPagination):
    page_size = 10