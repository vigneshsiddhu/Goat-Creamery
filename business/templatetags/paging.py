from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    query = context["request"].GET.copy()
    query["page"] = page_number
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else f"?page={page_number}"
