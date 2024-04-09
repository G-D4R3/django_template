from dataclasses import dataclass
from typing import Optional, Type
import urllib.parse as urlparse
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.reverse import reverse
from rest_framework.serializers import Serializer


@dataclass
class PaginationInfo:
    prev: Optional[str]
    next: Optional[str]
    total_count: int
    start: int
    end: int


class DefaultPaginator:
    class PageException(Exception):
        def __init__(self, message=None):
            self.message = message

    def __init__(self, queryset: QuerySet, url: str, request: Request, page=1, page_size=20, extra_params=None):
        self.queryset = queryset
        self.url = url
        self.request = request
        self.page = page
        self.page_size = page_size
        self.extra_params = {} if extra_params is None else extra_params

    def run(self, serializer_class: Type[Serializer]):
        pagination_info = self.pagination_info()

        paginator = Paginator(object_list=self.queryset, per_page=self.page_size)
        paginator.count = self.total_count
        paginated_data = paginator.get_page(self.page)

        serializer = serializer_class(paginated_data.object_list, many=True)

        return dict(
            total_count=pagination_info.total_count,
            prev=pagination_info.prev,
            next=pagination_info.next,
            results=serializer.data
        )

    def paginated_queryset(self) -> QuerySet:
        paginator = Paginator(object_list=self.queryset, per_page=self.page_size)
        paginated_memos = paginator.get_page(self.page)

        return paginated_memos.object_list

    def pagination_info(self):
        total_count: int = self.total_count
        page: int = self.page
        page_size: int = self.page_size

        start_idx: int = (page - 1) * page_size
        end_idx: int = page * page_size  # 포함 안됨.

        if total_count == 0 and page == 1:
            # 데이터가 하나도 없을 때
            return PaginationInfo(
                prev=None, next=None, total_count=total_count,
                start=start_idx, end=end_idx
            )

        url = reverse(self.url, request=self.request)
        prev_params = dict(page=page - 1, page_size=page_size, **self.extra_params)
        next_params = dict(page=page + 1, page_size=page_size, **self.extra_params)

        prev_url = None
        next_url = None
        if page == 1:
            prev_url = None
        else:
            prev_url = self.set_url_query_params(url, prev_params)
        if start_idx < total_count <= end_idx:
            next_url = None
        else:
            next_url = self.set_url_query_params(url, next_params)

        pagination_dto = PaginationInfo(
            prev=prev_url, next=next_url, total_count=total_count,
            start=start_idx, end=end_idx
        )
        return pagination_dto

    @staticmethod
    def set_url_query_params(url: str, query_params: dict):
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(query_params)
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    @property
    def total_count(self):
        if not hasattr(self, '_total_count'):
            self._total_count = self.queryset.count()
        return self._total_count
