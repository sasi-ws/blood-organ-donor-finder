from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import RegisterForm

MAX_LOGIN_ATTEMPTS = 5
LOCK_SECONDS = 300  # 5 minutes


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
        if user.role == "donor":
            messages.info(request, "Please complete your donor profile so people can find you.")
            return redirect("donors:edit_profile")
        return redirect("core:home")

    return render(request, "accounts/register.html", {"form": form})


class RateLimitedLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def _key(self):
        ip = self.request.META.get("REMOTE_ADDR", "unknown")
        username = self.request.POST.get("username", "").strip().lower()
        return f"login_fail:{ip}:{username}"

    def post(self, request, *args, **kwargs):
        if cache.get(self._key(), 0) >= MAX_LOGIN_ATTEMPTS:
            messages.error(
                request, "Too many failed attempts. Please wait 5 minutes and try again."
            )
            return self.render_to_response(self.get_context_data(form=self.get_form()))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._key()
        cache.set(key, cache.get(key, 0) + 1, LOCK_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._key())
        return super().form_valid(form)


@login_required
@require_http_methods(["GET", "POST"])
def delete_account(request):
    """Confirm, then permanently delete the user and all linked data."""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()  # related rows with on_delete=CASCADE are removed too
        messages.success(request, "Your account and all its data were deleted.")
        return redirect("core:home")
    return render(request, "accounts/delete_account.html")