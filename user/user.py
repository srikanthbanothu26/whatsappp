from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout


# Create your views here.
def register(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("user_login")

    return render(request, "register.html", {"form": form})


def login_view(request):
    # if the user is already logged in then redirect to the store page
    if request.user.is_authenticated:
        return redirect("user")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("user")

    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("user")
