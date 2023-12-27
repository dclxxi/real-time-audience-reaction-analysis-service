# Create your views here.
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from user.models import User


@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not re.match('^[a-zA-Z0-9]{6,15}$', userid):
            return render(request, 'user/signup.html', {'error': '아이디는 6~15자리의 영문자와 숫자로 이루어져야 합니다.'})

        if User.objects.filter(userid=userid).exists():
            return render(request, 'user/signup.html', {'error': '이미 존재하는 사용자 ID입니다.'})

        if len(password) < 8:
            return render(request, 'user/signup.html', {'error': '비밀번호는 최소 8자 이상이어야 합니다.'})

        count = 0
        if re.search('[0-9]', password):
            count += 1

        if re.search('[a-z]', password):
            count += 1

        if re.search('[A-Z]', password):
            count += 1

        if re.search('[^0-9a-zA-Z]', password):
            count += 1

        if count < 3:
            return render(request, 'user/signup.html', {'error': '비밀번호는 숫자, 소문자, 대문자, 특수 문자 중 최소 3가지를 포함해야 합니다.'})

        email_prefix = email.split('@')[0]
        if userid in password or name in password or email_prefix in password:
            return render(request, 'user/signup.html', {'error': '비밀번호에 개인 정보나 일반적인 단어를 사용할 수 없습니다.'})

        if password != password_confirm:
            return render(request, 'user/signup.html', {'error': '비밀번호가 일치하지 않습니다.'})

        user = User()
        user.userid = userid
        user.password = make_password(password)
        user.name = name
        user.email = email
        user.save()

        return HttpResponse("signup successful")

    return render(request, 'user/signup.html')


@csrf_exempt
def login_view(request):
    if request.method == 'GET':
        next_url = request.GET.get('next') or '/'
        return render(request, 'user/login.html', {'next': next_url})

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or '/'

        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return render(request, 'user/login.html', {'error': "존재하지 않는 아이디입니다."})

        user = authenticate(request, username=userid, password=password)

        if user is not None:
            login(request, user)

            if next_url.startswith("/live/record/"):
                return redirect("live:info")

            return redirect(next_url)
        else:
            return render(request, 'user/login.html', {'error': "비밀번호가 올바르지 않습니다."})


@csrf_exempt
def logout_view(request):
    logout(request)
    return HttpResponse("logout successful")
