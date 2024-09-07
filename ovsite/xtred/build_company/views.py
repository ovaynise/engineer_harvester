from django.shortcuts import render


def build_company(request):
    template_name = 'build_company/build_company.html'
    return render(request, template_name)
