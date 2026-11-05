from django.core.paginator import Paginator

DEFAULT_PER_PAGE = 20


class PagedList:
    def __init__(self, page):
        self._page = page

    def __bool__(self):
        return self._page.paginator.count > 0

    def __iter__(self):
        return iter(self._page)

    def __len__(self):
        return len(self._page)

    def __getattr__(self, name):
        return getattr(self._page, name)


def paginate(request, queryset, per_page=DEFAULT_PER_PAGE):
    page = Paginator(queryset, per_page).get_page(request.GET.get("page"))
    return PagedList(page)
