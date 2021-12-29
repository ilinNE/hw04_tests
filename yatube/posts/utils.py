from django.core.paginator import Paginator


def get_page_obj(obj_list, obj_per_page, request):
    paginator = Paginator(obj_list, obj_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
