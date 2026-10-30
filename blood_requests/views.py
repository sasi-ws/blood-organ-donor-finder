from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .alerts import send_alerts

from .forms import BloodRequestForm


@login_required
def post_request(request):
    if request.method == "POST":
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            blood_request.save()
            count = send_alerts(blood_request)
            messages.success(request, f"Your request was posted. {count} donor(s) alerted.")
            return redirect("blood_requests:post_request")
           
    else:
        form = BloodRequestForm(initial={"urgency": "normal"})
    return render(request, "blood_requests/post_request.html", {"form": form})
