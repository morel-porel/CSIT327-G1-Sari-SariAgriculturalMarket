# Suspension System Implementation Summary

## Overview
Comprehensive 3-level suspension system with automatic time-based lifting and role-specific penalties for vendors and consumers.

## Suspension Levels

### Level 1: First Suspension (2 Days)
**Vendors:**
- ❌ Cannot add or edit products
- ✅ Can still view their products
- 🕐 Automatically lifted after 2 days

**Consumers:**
- 💰 -100 loyalty points deducted
- ✅ Can still browse and add to cart
- 🕐 Automatically lifted after 2 days

---

### Level 2: Second Suspension (1 Week)
**Vendors:**
- ❌ Account unverified (loses vendor badge)
- 🗑️ ALL products deleted
- ⏳ Must wait 1 week before reapplying for verification
- 🕐 Suspension lifted after 1 week, but must reapply to become vendor again

**Consumers:**
- 💰 Additional -100 loyalty points (200 total)
- 🛒 CANNOT checkout or purchase products
- ✅ Can browse products
- 🕐 Automatically lifted after 1 week

---

### Level 3: Third Suspension (PERMANENT BAN)
**Both Vendors & Consumers:**
- 🚫 Permanent account ban
- ❌ Cannot log in
- ❌ Cannot access any features
- ⚠️ CANNOT BE REVERSED

---

## How Suspensions Are Triggered

1. **Admin sends 2 warnings** → User receives notification
2. **On 2nd warning** → First suspension is triggered automatically
3. **Each additional suspension** → Increases suspension level (1 → 2 → 3)

## Technical Implementation

### New Database Fields (CustomUser model)
```python
suspension_count = IntegerField(default=0)  # Tracks 0-3 suspensions
is_suspended = BooleanField(default=False)  # Currently suspended?
suspension_end_date = DateTimeField(null=True)  # When suspension ends
is_permanently_banned = BooleanField(default=False)  # 3rd suspension
```

### Key Files Created/Modified

1. **users/suspension_utils.py** (NEW)
   - `apply_suspension(user, reason)` - Main suspension logic
   - `check_and_lift_suspension(user)` - Auto-lift expired suspensions
   - `can_user_add_edit_products(user)` - Check vendor permissions
   - `can_user_checkout(user)` - Check consumer checkout ability
   - `deduct_loyalty_points(user, points)` - Penalty for consumers
   - `unverify_vendor_and_delete_products(user)` - Penalty for vendors

2. **users/middleware.py** (NEW)
   - Checks suspension status on every request
   - Auto-lifts expired suspensions
   - Blocks permanently banned users
   - Redirects suspended users to suspension info page

3. **users/models.py** (MODIFIED)
   - Added suspension tracking fields
   - Added helper methods: `is_suspension_active()`, `lift_suspension_if_expired()`

4. **dashboard/views.py** (MODIFIED)
   - Integrates with `apply_suspension()` for bulk actions
   - "Warn" action now triggers suspension system
   - "Ban" action immediately applies suspension

5. **products/views.py** (MODIFIED)
   - VendorRequiredMixin now checks `can_user_add_edit_products()`
   - Blocks suspended vendors from managing products

6. **pages/views.py** (MODIFIED)
   - checkout_api() checks `can_user_checkout()`
   - Blocks level 2+ suspended consumers from checkout

7. **templates/pages/suspension_info.html** (NEW)
   - Shows user their suspension status
   - Displays penalties and end date
   - Contact support button

8. **users/migrations/0015_suspension_system.py** (NEW)
   - Database migration for new fields

9. **settings.py** (MODIFIED)
   - Added SuspensionCheckMiddleware to MIDDLEWARE list

## Admin Dashboard Integration

### Bulk Actions Updated
- **Warn** → Increments warnings, triggers suspension at 2 warnings
- **Ban** → Immediately applies suspension (counts as reaching 2 warnings)
- **Delete Message** → Deletes message, notifies user (no suspension)
- **Resolve** → Marks resolved without action

### Reported Messages Display
Shows suspension status for each user:
- ⚠️ 0/2 (No warnings)
- ⚠️ 1/2 | Suspensions: 0/3 (1 warning)
- ⛔ SUSPENDED (1/3) (Currently suspended)
- 🚫 PERMANENTLY BANNED (3rd suspension)

## User Notifications

### Suspension Notifications
Users receive detailed notifications explaining:
- Why they were suspended
- How long the suspension lasts
- What penalties apply to their account
- When they can access the system again

### Auto-Lift Notifications
When suspension expires, users receive:
- "Your suspension has been lifted. Welcome back!"

## How It Works (Flow)

### Scenario 1: Vendor Gets Suspended
1. Admin warns vendor 2 times
2. **1st Suspension (2 days)**
   - Vendor cannot add/edit products
   - Gets notification with end date
3. After 2 days → Suspension auto-lifts
4. Vendor continues violating rules
5. **2nd Suspension (1 week)**
   - Account unverified
   - All products deleted
   - Must wait 1 week to reapply
6. After 1 week → Suspension lifts, but must reapply for vendor status
7. Vendor violates again
8. **3rd Suspension = PERMANENT BAN**

### Scenario 2: Consumer Gets Suspended
1. Admin warns consumer 2 times
2. **1st Suspension (2 days)**
   - 100 loyalty points deducted
   - Gets notification with end date
3. After 2 days → Suspension auto-lifts
4. Consumer continues violating rules
5. **2nd Suspension (1 week)**
   - Another 100 loyalty points deducted (200 total)
   - Cannot checkout products
6. After 1 week → Suspension lifts
7. Consumer violates again
8. **3rd Suspension = PERMANENT BAN**

## Testing the System

### To Run Migrations:
1. Double-click `run_migration.bat`
   OR
2. Open cmd and run:
   ```
   cd "c:\Users\User\Documents\IM2 Sari-Sari\CSIT327-G1-Sari-SariAgriculturalMarket"
   python manage.py makemigrations
   python manage.py migrate
   ```

### To Test Suspensions:
1. Log in as admin
2. Go to Reported Messages
3. Select a message report
4. Choose "Warn reported user(s)" and click Go
5. Give same user 2 warnings → triggers suspension
6. Check user's notifications → should see suspension notice
7. Try to log in as that user → should be blocked with message
8. Wait for suspension end date (or manually update in database)
9. Log in again → suspension should be lifted

### Manual Testing Commands (Django shell):
```python
from users.models import CustomUser
from users.suspension_utils import apply_suspension

# Get a user
user = CustomUser.objects.get(username='testuser')

# Apply 1st suspension
result = apply_suspension(user, "testing")
print(result)  # Shows level, duration, message

# Check status
print(user.suspension_count)  # Should be 1
print(user.is_suspended)  # Should be True
print(user.suspension_end_date)  # Should be 2 days from now

# Apply 2nd suspension
result = apply_suspension(user, "testing again")
# For vendors: products deleted, account unverified
# For consumers: -100 more points, cannot checkout

# Apply 3rd suspension
result = apply_suspension(user, "third strike")
print(user.is_permanently_banned)  # Should be True
```

## Important Notes

⚠️ **Permanent Bans Cannot Be Reversed** - Once a user reaches 3 suspensions, their account is permanently banned.

🕐 **Auto-Lift** - Suspensions are automatically lifted when the time expires. No admin action needed.

🔄 **Middleware Protection** - The middleware checks suspension status on every request, so suspended users cannot access the system even if they have a valid session.

💾 **Data Loss** - When vendors get 2nd suspension, their products are PERMANENTLY DELETED. This cannot be undone.

📧 **Notifications** - All suspension actions send detailed notifications to affected users explaining the situation.

## Future Enhancements (Optional)

- Email notifications in addition to in-app notifications
- Appeal system for users to contest suspensions
- Admin dashboard to view all suspended users
- Suspension history log
- Grace period for product recovery before deletion
- Temporary product hiding instead of deletion for 2nd suspension
