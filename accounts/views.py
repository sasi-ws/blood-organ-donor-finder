from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    # /accounts/register/?role=seeker pre-selects the role
    role = request.GET.get("role", "donor")
    form = RegisterForm(request.POST or None, initial={"role": role})

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account was created. Welcome!")
        # TODO (P2): send new donors to the donor profile page
        return redirect("core:home")

    return render(request, "accounts/register.html", {"form": form})