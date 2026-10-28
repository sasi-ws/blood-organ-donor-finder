from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import BloodRequestForm


@login_required
def post_request(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            messages.success(request, "Your request was posted.")
            # Temporary: we will redirect to the requests list once it exists.
            return redirect("blood_requests:post_request")
    else:
        form = BloodRequestForm(initial={"urgency": "normal"})
    return render(request, "blood_requests/post_request.html", {"form": form})
