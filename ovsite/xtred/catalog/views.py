from django.shortcuts import render


def detail(request, pk):
    template_name = 'catalog/detail.html'
    return render(request, template_name)


def list(request):
    template_name = 'catalog/list.html'
    return render(request, template_name)
