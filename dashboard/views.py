# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, VendorProfile
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.db import transaction 
from notifications.utils import create_notification # <--- NEW IMPORT

from messaging.models import MessageReport
from notifications.models import Notification

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    total_users = CustomUser.objects.count()
    total_vendors = CustomUser.objects.filter(role='VENDOR').count()
    total_sales_count = 0  
    total_sales_value = 0.00 
    
    report_data = [
        {'id': '001', 'type': 'Sales', 'value': '2025-10-26', 'status': 'Completed'},
        {'id': '002', 'type': 'User Report', 'value': '2025-10-25', 'status': 'Pending'},
    ]

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

    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        action = request.POST.get('action') # 'approve' or 'deny'
        
        try:
            profile = VendorProfile.objects.get(user_id=profile_id)
            user = profile.user
            
            if action == 'approve':
                with transaction.atomic():
                    profile.is_verified = True
                    profile.save()
                    user.role = 'VENDOR'
                    user.save()
                    
                    # Notify User of Approval
                    create_notification(
                        recipient=user,
                        message=f"Congratulations! Your shop '{profile.shop_name}' has been approved. You are now a Vendor.",
                        link="/my-products/"
                    )
                    messages.success(request, f"Approved {profile.shop_name}.")
                    
            elif action == 'deny':
                with transaction.atomic():
                    shop_name = profile.shop_name
                    # Notify User of Denial BEFORE deleting the profile reference
                    create_notification(
                        recipient=user,
                        message=f"Your vendor application for '{shop_name}' was denied. You may update your details and apply again.",
                        link="/become-vendor/"
                    )
                    
                    # Delete the pending profile so they can start fresh (or you could keep it with a 'denied' status flag if you modify models)
                    # For now, resetting is the cleanest way to handle "Deny" without schema changes.
                    profile.delete()
                    
                    # Ensure they are Consumer
                    user.role = 'CONSUMER'
                    user.save()
                    
                    messages.warning(request, f"Denied application for {shop_name}.")
                    
        except VendorProfile.DoesNotExist:
            messages.error(request, "Vendor profile not found.")

        return redirect('vendor_verification')

    # Split the lists
    pending_vendors = VendorProfile.objects.filter(is_verified=False).select_related('user')
    approved_vendors = VendorProfile.objects.filter(is_verified=True).select_related('user')
    
    context = {
        'pending_vendors': pending_vendors,
        'approved_vendors': approved_vendors,
    }
    return render(request, 'dashboard/vendor_verification.html', context)


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