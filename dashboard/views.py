# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, VendorProfile
from products.models import Product
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum
from notifications.utils import create_notification
from users.suspension_utils import apply_suspension

from messaging.models import MessageReport
from notifications.models import Notification

@login_required
def admin_dashboard_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Real user statistics
    total_users = CustomUser.objects.count()
    total_vendors = CustomUser.objects.filter(role='VENDOR').count()
    total_consumers = CustomUser.objects.filter(role='CONSUMER').count()
    
    # Product statistics
    total_products = Product.objects.count()
    total_products_value = Product.objects.aggregate(total=Sum('price'))['total'] or 0
    
    # Pending vendor applications
    pending_applications = VendorProfile.objects.filter(is_verified=False).count()
    
    # Reported messages
    unresolved_reports = MessageReport.objects.filter(is_resolved=False).count()
    
    # Chart data: Products created per day for the last 7 days
    today = timezone.now().date()
    chart_labels = []
    chart_data = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%b %d'))
        # Count products created on this date
        count = Product.objects.filter(
            created_at__date=date
        ).count()
        chart_data.append(count)
    
    # Recent activity for report table
    recent_products = Product.objects.select_related('vendor').order_by('-created_at')[:5]
    report_data = []
    for product in recent_products:
        report_data.append({
            'id': product.id,
            'type': 'Product Listed',
            'value': product.name,
            'status': f'By {product.vendor.username}',
            'date': product.created_at.strftime('%Y-%m-%d')
        })

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'total_consumers': total_consumers,
        'total_products': total_products,
        'total_products_value': f"₱{total_products_value:,.2f}",
        'pending_applications': pending_applications,
        'unresolved_reports': unresolved_reports,
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
        bulk_action = request.POST.get('bulk_action')
        selected_reports = request.POST.getlist('selected_reports')
        
        if not bulk_action:
            messages.error(request, "Please select an action.")
            return redirect('reported_messages')
        
        if not selected_reports:
            messages.error(request, "Please select at least one report.")
            return redirect('reported_messages')
        
        # Get the reports
        reports = MessageReport.objects.filter(id__in=selected_reports).select_related('message__sender')
        
        if bulk_action == 'warn':
            # Warn users - this now triggers suspension system
            warned_users = set()
            suspended_results = []
            
            with transaction.atomic():
                for report in reports:
                    offending_user = report.message.sender
                    
                    # Skip if already processed
                    if offending_user.id in warned_users:
                        continue
                    
                    warned_users.add(offending_user.id)
                    offending_user.warning_count += 1
                    
                    if offending_user.warning_count >= 2:
                        # Apply suspension when warnings reach 2
                        result = apply_suspension(offending_user, reason="inappropriate messages")
                        suspended_results.append({
                            'username': offending_user.username,
                            'level': result['level'],
                            'duration': result['duration']
                        })
                    else:
                        offending_user.save()
                        warnings_left = 2 - offending_user.warning_count
                        
                        create_notification(
                            recipient=offending_user,
                            message=f"Warning {offending_user.warning_count}/2: Your message violated our community guidelines. You have {warnings_left} warning(s) remaining before suspension.",
                            link=None
                        )
                    
                    # Mark report as resolved
                    report.is_resolved = True
                    report.moderator = request.user
                    report.resolved_at = timezone.now()
                    report.moderation_action = 'warn'
                    report.resolution_notes = f"User warned. Total warnings: {offending_user.warning_count}"
                    report.save()
            
            if suspended_results:
                for result in suspended_results:
                    messages.warning(request, f"{result['username']}: Suspension Level {result['level']} ({result['duration']})")
            messages.success(request, f"Warned {len(warned_users)} user(s) and resolved {len(selected_reports)} report(s).")
        
        elif bulk_action == 'resolve':
            # Mark as resolved without action
            with transaction.atomic():
                for report in reports:
                    report.is_resolved = True
                    report.moderator = request.user
                    report.resolved_at = timezone.now()
                    report.moderation_action = 'none'
                    report.resolution_notes = "Marked as resolved without action."
                    report.save()
            messages.success(request, f"Marked {len(selected_reports)} report(s) as resolved.")
        
        elif bulk_action == 'delete_message':
            # Delete messages and notify users
            with transaction.atomic():
                notified_users = set()
                for report in reports:
                    report.message.is_moderator_deleted = True
                    report.message.save()
                    
                    report.is_resolved = True
                    report.moderator = request.user
                    report.resolved_at = timezone.now()
                    report.moderation_action = 'delete'
                    report.resolution_notes = "Original message deleted by moderator."
                    report.save()
                    
                    # Send notification only once per user
                    if report.message.sender.id not in notified_users:
                        create_notification(
                            recipient=report.message.sender,
                            message=f"Your message was deleted by a moderator for violating community guidelines.",
                            link=None
                        )
                        notified_users.add(report.message.sender.id)
            
            messages.success(request, f"Deleted {len(selected_reports)} message(s) and notified {len(notified_users)} user(s).")
        
        elif bulk_action == 'delete_report':
            # Delete the reports entirely
            count = reports.count()
            reports.delete()
            messages.success(request, f"Deleted {count} report(s).")
        
        elif bulk_action == 'ban':
            # Immediately suspend users (triggers suspension system)
            banned_users = []
            
            with transaction.atomic():
                for report in reports:
                    offending_user = report.message.sender
                    
                    # Skip if already processed
                    if any(b['username'] == offending_user.username for b in banned_users):
                        continue
                    
                    # Set warning count to 2 to trigger suspension
                    offending_user.warning_count = 2
                    result = apply_suspension(offending_user, reason="severe community guidelines violation")
                    
                    banned_users.append({
                        'username': offending_user.username,
                        'level': result['level']
                    })
                    
                    # Mark report as resolved
                    report.is_resolved = True
                    report.moderator = request.user
                    report.resolved_at = timezone.now()
                    report.moderation_action = 'ban'
                    report.resolution_notes = f"User suspended immediately (Level {result['level']})."
                    report.save()
            
            for user_info in banned_users:
                messages.warning(request, f"{user_info['username']}: Suspension Level {user_info['level']}")
            messages.success(request, f"Applied suspensions to {len(banned_users)} user(s) and resolved {len(selected_reports)} report(s).")

        return redirect('reported_messages')

    reports = MessageReport.objects.all().select_related(
        'reporter', 
        'message__sender',
        'moderator'
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


@login_required
def vendor_list_view(request):
    """Admin view to manage all vendors with bulk suspension actions"""
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        bulk_action = request.POST.get('bulk_action')
        selected_vendors = request.POST.getlist('selected_vendors')
        
        if not bulk_action:
            messages.error(request, "Please select an action.")
            return redirect('vendor_list')
        
        if not selected_vendors:
            messages.error(request, "Please select at least one vendor.")
            return redirect('vendor_list')
        
        # Get the vendor users
        vendors = CustomUser.objects.filter(id__in=selected_vendors, role='VENDOR')
        
        if bulk_action == 'suspend_1':
            # Apply 1st suspension (2 days)
            suspended_count = 0
            with transaction.atomic():
                for vendor in vendors:
                    # Set to 1 warning so next suspension will be level 1
                    if vendor.suspension_count == 0:
                        vendor.warning_count = 2  # Trigger suspension
                        result = apply_suspension(vendor, reason="admin action")
                        suspended_count += 1
            messages.success(request, f"Applied 1st suspension (2 days) to {suspended_count} vendor(s).")
        
        elif bulk_action == 'suspend_2':
            # Apply 2nd suspension (1 week + unverify + delete products)
            suspended_count = 0
            with transaction.atomic():
                for vendor in vendors:
                    if vendor.suspension_count < 2:
                        # Force to 2nd suspension
                        vendor.suspension_count = 1
                        vendor.warning_count = 2
                        vendor.save()
                        result = apply_suspension(vendor, reason="admin action - severe violation")
                        suspended_count += 1
            messages.warning(request, f"Applied 2nd suspension (1 week, unverified, products deleted) to {suspended_count} vendor(s).")
        
        elif bulk_action == 'ban':
            # Permanent ban (3rd suspension)
            banned_count = 0
            with transaction.atomic():
                for vendor in vendors:
                    if not vendor.is_permanently_banned:
                        # Force to 3rd suspension (permanent ban)
                        vendor.suspension_count = 2
                        vendor.warning_count = 2
                        vendor.save()
                        result = apply_suspension(vendor, reason="admin action - permanent ban")
                        banned_count += 1
            messages.error(request, f"PERMANENTLY BANNED {banned_count} vendor(s). This cannot be undone.")
        
        elif bulk_action == 'lift_suspension':
            # Lift suspension and restore access
            lifted_count = 0
            with transaction.atomic():
                for vendor in vendors:
                    if vendor.is_suspended and not vendor.is_permanently_banned:
                        vendor.is_suspended = False
                        vendor.suspension_end_date = None
                        vendor.is_active = True
                        vendor.save()
                        
                        create_notification(
                            recipient=vendor,
                            message="Your suspension has been lifted by an administrator. Please follow our community guidelines.",
                            link=None
                        )
                        lifted_count += 1
            messages.success(request, f"Lifted suspension for {lifted_count} vendor(s).")
        
        elif bulk_action == 'reset_warnings':
            # Reset warnings to 0
            reset_count = 0
            with transaction.atomic():
                for vendor in vendors:
                    if vendor.warning_count > 0:
                        vendor.warning_count = 0
                        vendor.save()
                        
                        create_notification(
                            recipient=vendor,
                            message="Your warnings have been reset to 0 by an administrator. This is a fresh start - please follow our guidelines.",
                            link=None
                        )
                        reset_count += 1
            messages.success(request, f"Reset warnings to 0 for {reset_count} vendor(s).")

        return redirect('vendor_list')

    # Get all vendors with their profiles and product counts
    from django.db.models import Count
    vendors = VendorProfile.objects.select_related('user').annotate(
        product_count=Count('user__product')
    ).order_by('-user__date_joined')
    
    context = {
        'vendors': vendors
    }
    return render(request, 'dashboard/vendor_list.html', context)