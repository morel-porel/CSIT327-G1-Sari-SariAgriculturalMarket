# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, VendorProfile
from datetime import datetime, timedelta

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