from django.shortcuts import redirect
from django.contrib import messages
from .utils import create_notification

def test_notification_view(request):
    if request.user.is_authenticated:
        create_notification(
            recipient=request.user,
            message="This is a test notification!",
            link="/about/"
        )
        messages.success(request, "Test notification created!")
    return redirect('home')