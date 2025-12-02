# users/suspension_utils.py
from django.utils import timezone
from datetime import timedelta
from notifications.utils import create_notification

def apply_suspension(user, reason="community guidelines violation"):
    """
    Apply suspension based on user's current suspension count.
    
    Suspension levels:
    1st: 2 days suspension
    2nd: 1 week suspension + role-specific penalties
    3rd: Permanent ban
    """
    user.suspension_count += 1
    user.is_suspended = True
    
    if user.suspension_count == 1:
        # First suspension: 2 days
        user.suspension_end_date = timezone.now() + timedelta(days=2)
        user.is_active = False
        user.save()
        
        create_notification(
            recipient=user,
            message=f"Your account has been SUSPENDED for 2 days due to {reason}. You can access your account again after {user.suspension_end_date.strftime('%B %d, %Y at %I:%M %p')}.",
            link=None
        )
        
        # Role-specific actions for 1st suspension
        if user.role == 'VENDOR':
            # Vendors cannot add/edit products (handled in views)
            create_notification(
                recipient=user,
                message="During suspension, you cannot add or edit products.",
                link=None
            )
        elif user.role == 'CONSUMER':
            # Deduct 100 loyalty points
            deduct_loyalty_points(user, 100)
            create_notification(
                recipient=user,
                message="100 loyalty points have been deducted from your account.",
                link=None
            )
        
        return {
            'level': 1,
            'duration': '2 days',
            'can_be_lifted': True,
            'message': f'User suspended for 2 days (1st suspension)'
        }
    
    elif user.suspension_count == 2:
        # Second suspension: 1 week
        user.suspension_end_date = timezone.now() + timedelta(weeks=1)
        user.is_active = False
        user.save()
        
        create_notification(
            recipient=user,
            message=f"Your account has been SUSPENDED for 1 WEEK due to repeated violations. You can access your account again after {user.suspension_end_date.strftime('%B %d, %Y at %I:%M %p')}.",
            link=None
        )
        
        # Role-specific actions for 2nd suspension
        if user.role == 'VENDOR':
            # Unverify vendor and delete products
            unverify_vendor_and_delete_products(user)
            create_notification(
                recipient=user,
                message="Your vendor account has been unverified and all products have been removed. You must wait 1 week and reapply for verification.",
                link="/become-vendor/"
            )
        elif user.role == 'CONSUMER':
            # Deduct another 100 loyalty points and block checkout
            deduct_loyalty_points(user, 100)
            create_notification(
                recipient=user,
                message="100 loyalty points have been deducted. You cannot checkout products during this suspension.",
                link=None
            )
        
        return {
            'level': 2,
            'duration': '1 week',
            'can_be_lifted': True,
            'message': f'User suspended for 1 week (2nd suspension)'
        }
    
    else:  # suspension_count >= 3
        # Third suspension: Permanent ban
        user.is_permanently_banned = True
        user.is_active = False
        user.suspension_end_date = None  # No end date for permanent ban
        user.save()
        
        create_notification(
            recipient=user,
            message="Your account has been PERMANENTLY BANNED due to repeated serious violations of our community guidelines. This action cannot be reversed.",
            link=None
        )
        
        # Role-specific actions for permanent ban
        if user.role == 'VENDOR':
            # Unverify and delete all products
            unverify_vendor_and_delete_products(user)
        
        return {
            'level': 3,
            'duration': 'Permanent',
            'can_be_lifted': False,
            'message': f'User permanently banned (3rd suspension)'
        }


def deduct_loyalty_points(user, points):
    """Deduct loyalty points from consumer"""
    try:
        from users.models import LoyaltyProfile
        loyalty_profile = LoyaltyProfile.objects.get(user=user)
        loyalty_profile.points = max(0, loyalty_profile.points - points)  # Don't go below 0
        loyalty_profile.update_rank()
        loyalty_profile.save()
    except LoyaltyProfile.DoesNotExist:
        # Create profile if it doesn't exist
        from users.models import LoyaltyProfile
        LoyaltyProfile.objects.create(user=user, points=0)


def unverify_vendor_and_delete_products(user):
    """Unverify vendor account and delete all their products"""
    try:
        from users.models import VendorProfile
        from products.models import Product
        
        vendor_profile = VendorProfile.objects.get(user=user)
        
        # Delete all products
        products_count = Product.objects.filter(vendor=user).count()
        Product.objects.filter(vendor=user).delete()
        
        # Unverify vendor
        vendor_profile.is_verified = False
        vendor_profile.save()
        
        # Change role back to consumer
        user.role = 'CONSUMER'
        user.save()
        
        return products_count
    except VendorProfile.DoesNotExist:
        return 0


def check_and_lift_suspension(user):
    """
    Check if suspension period has ended and lift it automatically.
    Should be called when user tries to log in or access the system.
    """
    if user.is_permanently_banned:
        return False  # Cannot lift permanent ban
    
    if user.is_suspended and user.suspension_end_date:
        if timezone.now() >= user.suspension_end_date:
            # Lift suspension
            user.is_suspended = False
            user.suspension_end_date = None
            user.is_active = True
            user.save()
            
            create_notification(
                recipient=user,
                message="Your suspension period has ended. Welcome back! Please follow our community guidelines.",
                link=None
            )
            return True
    
    return False


def can_user_add_edit_products(user):
    """Check if vendor can add or edit products"""
    if user.role != 'VENDOR':
        return False
    
    if user.is_permanently_banned:
        return False
    
    if user.is_suspended:
        return False
    
    try:
        from users.models import VendorProfile
        vendor_profile = VendorProfile.objects.get(user=user)
        return vendor_profile.is_verified
    except VendorProfile.DoesNotExist:
        return False


def can_user_checkout(user):
    """Check if consumer can checkout products"""
    if user.is_permanently_banned:
        return False
    
    # Cannot checkout during 2nd or 3rd suspension
    if user.is_suspended and user.suspension_count >= 2:
        return False
    
    return True


def get_suspension_status_message(user):
    """Get a human-readable suspension status message"""
    if user.is_permanently_banned:
        return "Permanently Banned"
    
    if user.is_suspended and user.suspension_end_date:
        time_remaining = user.suspension_end_date - timezone.now()
        days = time_remaining.days
        hours = time_remaining.seconds // 3600
        
        if days > 0:
            return f"Suspended for {days} more day(s)"
        elif hours > 0:
            return f"Suspended for {hours} more hour(s)"
        else:
            return "Suspension ending soon"
    
    return f"Active (Suspensions: {user.suspension_count}/3)"
