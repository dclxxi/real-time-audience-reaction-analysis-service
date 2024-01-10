from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from report.models import Feedback


# Create your views here.
@csrf_exempt
def main(request):
    return render(request, "main.html")


def error404(request):
    return render(request, "error/../templates/404.html", status=404)


def error500(request):
    return render(request, "error/../templates/500.html", status=500)
