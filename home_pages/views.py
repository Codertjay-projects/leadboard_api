from django.shortcuts import render


def home_page(request):
    return render(request, 'HomePage/home_page.html', )


def view_503(request, exception=None):
    return render(request, 'errors/503.html', status=503)
