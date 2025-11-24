# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, VendorProfile
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.db import transaction 

# Import your models
from messaging.models import MessageReport
from notifications.models import Notification

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    # --- Calculate Analytics Overview data ---
    total_users = CustomUser.objects.count()
    total_vendors = CustomUser.objects.filter(role='VENDOR').count()

    # --- PLACEHOLDER DATA ---
    total_sales_count = 0  
    total_sales_value = 0.00 
    
    report_data = [
        {'id': '001', 'type': 'Sales', 'value': '2025-10-26', 'status': 'Completed'},
        {'id': '002', 'type': 'User Report', 'value': '2025-10-25', 'status': 'Pending'},
    ]

    # --- PREPARE DATA FOR THE SALES TREND CHART ---
    today = datetime.now()
    chart_labels = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    chart_data = [0, 0, 0, 0, 0, 0, 0]

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_sales_count': total_sales_count,
        'total_sales_value': f"₱{total_sales_value:,.2f}",
        'report_data': report_data,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

def vendor_verification_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Handle the verification update
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        
        try:
            profile = VendorProfile.objects.get(user_id=profile_id)
            user = profile.user
            
            with transaction.atomic():
                # 1. Toggle the verification status
                new_status = not profile.is_verified
                profile.is_verified = new_status
                profile.save()

                # 2. AUTOMATICALLY UPDATE USER ROLE
                if new_status:
                    user.role = 'VENDOR'
                    messages.success(request, f"Approved {profile.shop_name}! User is now a Vendor.")
                else:
                    user.role = 'CONSUMER'
                    messages.warning(request, f"Revoked approval for {profile.shop_name}. User reverted to Consumer.")
                
                user.save()

        except VendorProfile.DoesNotExist:
            messages.error(request, "Vendor profile not found.")

        return redirect('vendor_verification')

    # Get all vendors for display
    all_vendors = VendorProfile.objects.all().select_related('user')
    
    context = {
        'vendors': all_vendors
    }
    return render(request, 'dashboard/vendor_verification.html', context)


# --- VIEW FOR REPORTED MESSAGES ---

@login_required
def reported_messages_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        try:
            report = MessageReport.objects.get(id=report_id)
        except MessageReport.DoesNotExist:
            return redirect('reported_messages')

        # Delete stuck notifications logic
        try:
            offending_user = report.message.sender
            notifications_to_delete = Notification.objects.filter(
                recipient=offending_user,
                message__startswith="Warning: Your message,",
                link__isnull=True
            )
            if notifications_to_delete.exists():
                notifications_to_delete.delete()
        except Exception as e:
            print(f"Error deleting user warning notifications: {e}")

        if 'action_resolve' in request.POST:
            report.is_resolved = True
            report.moderator = request.user
            report.resolved_at = timezone.now()
            report.resolution_notes = "Marked as resolved from dashboard."
            report.save()
        
        elif 'action_delete_report' in request.POST:
            report.delete()

        elif 'action_delete_message' in request.POST:
            report.message.is_moderator_deleted = True
            report.message.save()
            report.is_resolved = True
            report.moderator = request.user
            report.resolved_at = timezone.now()
            report.resolution_notes = "Original message deleted by moderator."
            report.save()

        return redirect('reported_messages')

    reports = MessageReport.objects.all().select_related(
        'reporter', 
        'message__sender'
    ).order_by('is_resolved', '-reported_at')
    
    context = {
        'reports': reports
    }
    return render(request, 'dashboard/reported_messages.html', context)


# --- NEW VIEW TO CLEAR *ALL* STUCK WARNINGS ---
@login_required
def clear_all_warnings_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        warnings_to_delete = Notification.objects.filter(
            message__startswith="Warning: Your message,",
            link__isnull=True
        )
        
        count = warnings_to_delete.count()
        if count > 0:
            warnings_to_delete.delete()
            messages.success(request, f"Successfully cleared {count} stuck warning notifications.")
        else:
            messages.info(request, "No stuck warning notifications were found.")
            
        return redirect('reported_messages')

    return redirect('reported_messages')