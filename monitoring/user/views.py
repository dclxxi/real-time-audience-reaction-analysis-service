# Create your views here.
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from user.models import User


@csrf_exempt
def signup_view(request):
    if request.method == "GET":
        return render(request, "user/sign_up.html")

    if request.method == "POST":
        userid = request.POST.get("userid")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        name = request.POST.get("name")
        email = request.POST.get("email")

        error_message = validate_signup_data(userid, password, password_confirm, name, email)
        if error_message:
            return render(request, "user/sign_up.html", {"error": error_message})

        user = User(
            userid=userid,
            password=make_password(password),
            name=name,
            email=email
        )
        user.save()

        return redirect("user:login")


def validate_signup_data(userid, password, password_confirm, name, email):
    return (
            validate_userid(userid) or
            validate_password(password, userid, name, email) or
            validate_password_confirmation(password, password_confirm)
    )


def validate_userid(userid):
    if not userid or not re.match("^[a-zA-Z0-9]{6,15}$", userid):
        return "아이디는 6~15자리의 영문자와 숫자로 이루어져야 합니다."

    if User.objects.filter(username=userid).exists():
        return "이미 존재하는 사용자 ID입니다."

    return None


def validate_password(password, userid, name, email):
    if not password or len(password) < 8:
        return "비밀번호는 최소 8자 이상이어야 합니다."

    patterns = ["[0-9]", "[a-z]", "[A-Z]", "[^0-9a-zA-Z]"]
    if sum(bool(re.search(pattern, password)) for pattern in patterns) < 3:
        return "비밀번호는 숫자, 소문자, 대문자, 특수 문자 중 최소 3가지를 포함해야 합니다."

    email_prefix = email.split("@")[0]
    if any(info.lower() in password.lower() for info in [userid, name, email_prefix]):
        return "비밀번호에 개인 정보나 일반적인 단어를 사용할 수 없습니다."

    return None


def validate_password_confirmation(password, password_confirm):
    if password != password_confirm:
        return "비밀번호가 일치하지 않습니다."

    return None


@csrf_exempt
def login_view(request):
    if request.method == "GET":
        next_url = request.GET.get("next") or "/"
        return render(request, "user/login_page.html", {"next": next_url})

    if request.method == "POST":
        userid = request.POST.get("userid")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")
        next_url = request.POST.get("next") or "/"

        if userid == "" or password == "":
            return render(request, "user/login_page.html")

        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return render(request, "user/login_page.html", {"error": "존재하지 않는 아이디입니다."})

        user = authenticate(request, username=userid, password=password)

        if user is not None:
            login(request, user)

            if remember_me is not None:
                request.session.set_expiry(3600 * 24 * 30)  # 30일 동안 유효한 세션
            else:
                request.session.set_expiry(0)

            if next_url.startswith("/live/record/"):
                return redirect("live:info")

            return redirect(next_url)
        else:
            return render(
                request, "user/login_page.html", {"error": "비밀번호가 올바르지 않습니다."}
            )


@csrf_exempt
def logout_view(request):
    logout(request)
    return redirect("/")
