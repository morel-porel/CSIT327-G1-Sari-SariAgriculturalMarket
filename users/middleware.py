# users/middleware.py
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from users.suspension_utils import check_and_lift_suspension


class SuspensionCheckMiddleware:
    """
    Middleware to check if user's suspension has expired and lift it automatically.
    Also blocks suspended users from accessing the system.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Check if suspension has expired
            if check_and_lift_suspension(request.user):
                messages.success(request, "Your suspension has been lifted. Welcome back!")
            
            # Block permanently banned users
            if request.user.is_permanently_banned:
                # Allow logout
                if request.path != '/logout/':
                    messages.error(request, "Your account has been permanently banned.")
                    return redirect('logout')
            
            # Block suspended users (except from logout and suspension info pages)
            if request.user.is_suspended and request.path not in ['/logout/', '/suspension-info/']:
                if request.user.suspension_end_date:
                    time_remaining = request.user.suspension_end_date - timezone.now()
                    days = time_remaining.days
                    hours = time_remaining.seconds // 3600
                    
                    if days > 0:
                        messages.error(request, f"Your account is suspended for {days} more day(s).")
                    else:
                        messages.error(request, f"Your account is suspended for {hours} more hour(s).")
                else:
                    messages.error(request, "Your account is currently suspended.")
                
                return redirect('logout')
        
        response = self.get_response(request)
        return response
