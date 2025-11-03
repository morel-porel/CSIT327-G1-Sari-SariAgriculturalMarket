# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, VendorProfile
from datetime import datetime, timedelta
from django.utils import timezone  # Import timezone
from django.contrib import messages  # <-- IMPORT THIS

# Import your models
from messaging.models import MessageReport
from notifications.models import Notification

@login_required
def admin_dashboard_view(request):
    # Security check: only superusers can access this page
    if not request.user.is_superuser:
        return redirect('home')

    # --- Calculate Analytics Overview data ---
    total_users = CustomUser.objects.count()
    total_vendors = CustomUser.objects.filter(role='VENDOR').count()

    # --- PLACEHOLDER DATA ---
    # Once you have an 'Order' model, you can calculate these properly.
    total_sales_count = 0  # Replace with: Order.objects.count()
    total_sales_value = 0.00 # Replace with: Order.objects.aggregate(total=Sum('price'))['total']
    
    # --- PLACEHOLDER DATA ---
    # This assumes you'll have a model for reports later
    report_data = [
        {'id': '001', 'type': 'Sales', 'value': '2025-10-26', 'status': 'Completed'},
        {'id': '002', 'type': 'User Report', 'value': '2025-10-25', 'status': 'Pending'},
    ]

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_sales_count': total_sales_count,
        'total_sales_value': f"₱{total_sales_value:,.2f}", # Formats the number
        'report_data': report_data,
    }

    # --- PREPARE DATA FOR THE SALES TREND CHART ---
    # For now, we'll generate labels for the last 7 days and use placeholder data.
    # This can be replaced with real database queries later.
    today = datetime.now()
    chart_labels = [(today - timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    
    # Placeholder data showing a slight upward trend. If you have no sales, this could be all zeros.
    chart_data = [0, 0, 0, 0, 0, 0, 0] # Replace with real sales data later

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_sales_count': total_sales_count,
        'total_sales_value': f"₱{total_sales_value:,.2f}",
        'report_data': report_data,
        
        # --- PASS THE CHART DATA TO THE TEMPLATE ---
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
        profile = VendorProfile.objects.get(user_id=profile_id)
        profile.is_verified = not profile.is_verified # Toggle the status
        profile.save()
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

    # Handle POST requests for actions
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        
        try:
            report = MessageReport.objects.get(id=report_id)
        except MessageReport.DoesNotExist:
            # Report might have been deleted in another tab, just redirect
            return redirect('reported_messages')

        # --- THIS LOGIC PREVENTS *NEW* STUCK NOTIFICATIONS ---
        try:
            # Get the user who sent the offending message
            offending_user = report.message.sender
            
            # Find all "Warning" notifications for this user (which have no link)
            notifications_to_delete = Notification.objects.filter(
                recipient=offending_user,
                message__startswith="Warning: Your message,",
                link__isnull=True
            )
            
            # Delete them all
            if notifications_to_delete.exists():
                notifications_to_delete.delete()
                
        except Exception as e:
            # If this fails, we still want the admin action to complete.
            print(f"Error deleting user warning notifications for report {report_id}: {e}")
        # --- END NOTIFICATION LOGIC ---


        if 'action_resolve' in request.POST:
            # Mark the report as resolved
            report.is_resolved = True
            report.moderator = request.user
            report.resolved_at = timezone.now()
            report.resolution_notes = "Marked as resolved from dashboard."
            report.save()
        
        elif 'action_delete_report' in request.POST:
            # Delete the report itself
            # The notifications are already deleted from the logic above.
            report.delete()

        elif 'action_delete_message' in request.POST:
            # Soft-delete the original message
            report.message.is_moderator_deleted = True
            report.message.save()
            # And also resolve the report
            report.is_resolved = True
            report.moderator = request.user
            report.resolved_at = timezone.now()
            report.resolution_notes = "Original message deleted by moderator."
            report.save()

        return redirect('reported_messages')

    # Get all reports, pre-fetching related user data for efficiency
    reports = MessageReport.objects.all().select_related(
        'reporter', 
        'message__sender'
    ).order_by('is_resolved', '-reported_at') # Show unresolved first
    
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
        # Find ALL moderation warnings in the entire database
        # These are defined as having a message starting with "Warning:"
        # AND having no link (link__isnull=True)
        #
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

    # If GET request, just go back to the reports page
    return redirect('reported_messages')