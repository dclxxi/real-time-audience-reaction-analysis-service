# Create your views here.
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from user.models import User


@csrf_exempt
def signup(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        name = request.POST.get('name')
        email = request.POST.get('email')

        if User.objects.filter(userid=userid).exists():
            return render(request, 'user/signup.html')

        if password != password_confirm:
            return render(request, 'user/signup.html')

        user = User()
        user.userid = userid
        user.password = make_password(password)  # 비밀번호 암호화
        user.name = name
        user.email = email
        user.save()

        return HttpResponse("signup successful")

    return render(request, 'user/signup.html')


@csrf_exempt
def login(request):
    if request.method == 'GET':
        return render(request, 'user/login.html')

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')

        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return render(request, 'user/login.html')

        if check_password(password, user.password):
            return HttpResponse("login successful")
        else:
            print("error: password")
            return render(request, 'user/login.html')
