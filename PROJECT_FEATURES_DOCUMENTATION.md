# 🌾 Sari-Sari Agricultural Market - Complete Feature Documentation

**Project:** Sari-Sari: Agricultural Market Platform  
**Purpose:** Connect small-scale agricultural vendors directly with consumers in Cebu City  
**Tech Stack:** Django 5.2.6, PostgreSQL (Supabase), HTML5, CSS3, JavaScript  

---

## 📑 TABLE OF CONTENTS

1. [User Authentication & Authorization](#1-user-authentication--authorization)
2. [User Profile Management](#2-user-profile-management)
3. [Vendor Verification System](#3-vendor-verification-system)
4. [Product Management](#4-product-management)
5. [Shopping & Cart System](#5-shopping--cart-system)
6. [Search & Discovery](#6-search--discovery)
7. [Messaging System](#7-messaging-system)
8. [Notification System](#8-notification-system)
9. [Loyalty Rewards Program](#9-loyalty-rewards-program)
10. [Content Moderation & Safety](#10-content-moderation--safety)
11. [User Suspension System](#11-user-suspension-system)
12. [Admin Dashboard](#12-admin-dashboard)
13. [UI/UX Features](#13-uiux-features)

---

## 1. USER AUTHENTICATION & AUTHORIZATION

### 1.1 Dual Role Registration System
**Implementation:** `users/views.py`, `users/forms.py`

**Features:**
- **Consumer Registration** (`consumer_signup_view`)
  - Username, email, password creation
  - Automatic role assignment as 'CONSUMER'
  - Auto-login after successful registration
  - Form: `ConsumerSignUpForm`

- **Vendor Registration** (`vendor_signup_view`)
  - Separate registration flow for vendors
  - Initial account creation with 'VENDOR' role
  - Must complete vendor verification to sell products
  - Form: `VendorSignUpForm`

**Key Models:**
```python
CustomUser(AbstractUser):
  - role: VENDOR | CONSUMER
  - phone_number, date_of_birth, avatar
  - address, city, zip_code
  - warning_count, suspension_count
  - is_suspended, suspension_end_date
  - is_permanently_banned
```

### 1.2 Login System
**Implementation:** `users/views.py` - `login_view()`

**Features:**
- Username/password authentication
- Role-based redirection:
  - Superuser → Admin Dashboard
  - Vendor → Home page
  - Consumer → Home page
- Custom login template with placeholders
- Session management

### 1.3 Logout System
**Implementation:** `users/views.py` - `logout_view()`

**Features:**
- Session cleanup
- Success message notification
- Redirect to login page

### 1.4 Authorization Controls
**Implementation:** `@login_required` decorators, `UserPassesTestMixin`

**Features:**
- Login-required views for protected content
- Role-based access control (RBAC)
- Vendor-only product management
- Admin-only dashboard access

---

## 2. USER PROFILE MANAGEMENT

### 2.1 Consumer Profile
**Implementation:** `users/views.py` - `profile_view()`, `templates/pages/consumer_profile.html`

**Features:**
- **View & Edit Personal Information:**
  - First name, last name
  - Email, phone number
  - Date of birth
  - Complete address (street, city, zip code)
  - Profile avatar upload
  
- **Password Change:**
  - Secure password update
  - Session preservation after change
  - Old password verification

**Form:** `ConsumerProfileForm` with file upload support

### 2.2 Vendor Profile
**Implementation:** `users/views.py` - `vendor_profile_view()`, `VendorProfile` model

**Features:**
- **Vendor-Specific Information:**
  - Shop name and description
  - Business permit number
  - Contact number
  - Profile image upload
  - Farming practices description
  - Years of experience
  
- **Business Address:**
  - Pickup address (with landmark)
  - Barangay selection
  - City and zip code
  - Region selection (13 Cebu locations)

**Model:**
```python
VendorProfile:
  - shop_name, business_permit_number
  - is_verified (verification status)
  - contact_number, profile_image
  - shop_description, farming_practices
  - experience_years
  - pickup_address, barangay, city, zip_code
  - region (Cebu City, Mandaue, Lapu-Lapu, etc.)
```

### 2.3 Public Vendor Profile View
**Implementation:** `users/views.py` - `consumer_vendor_profile_view()`

**Features:**
- Consumers can view vendor public profiles
- Displays shop information and verification badge
- Shows farming practices and experience
- Contact information display
- API endpoint: `vendor_detail_api()` for AJAX requests

---

## 3. VENDOR VERIFICATION SYSTEM

### 3.1 Vendor Onboarding Flow (3-Step Process)
**Implementation:** `users/views.py` - Multi-step wizard

**Step 1: Business Information** (`vendor_onboarding_step1`)
- Shop name (required)
- Contact number
- Shop address (pickup location)
- Barangay, city, zip code
- Shop description
- Form: `VendorStep1Form`

**Step 2: Personal Details** (`vendor_onboarding_step2`)
- Owner's first and last name
- Date of birth
- Profile image upload
- Farming practices description
- Years of experience
- Forms: `VendorStep2UserForm`, `VendorStep2ProfileForm`

**Step 3: Review & Submit** (`vendor_onboarding_step3`)
- Preview all entered information
- Final submission confirmation
- Notification sent to user confirming submission
- Success page redirect

**Success Page** (`vendor_onboarding_success`)
- Confirmation message
- Information about pending admin review
- Cannot sell products until verified

### 3.2 Admin Verification Process
**Implementation:** `dashboard/views.py` - `vendor_verification_view()`

**Features:**
- **Pending Applications View:**
  - List of unverified vendor applications
  - View all submitted information
  - Approve or Deny actions

- **Approve Action:**
  - Sets `is_verified = True`
  - Confirms `role = 'VENDOR'`
  - Sends approval notification to vendor
  - Vendor can now add/manage products

- **Deny Action:**
  - Deletes vendor profile
  - Reverts user role to 'CONSUMER'
  - Sends denial notification
  - User can reapply with updated information

- **Approved Vendors List:**
  - View of all verified vendors
  - Shop details and contact information
  - Verification status display

**Database Transaction:** Uses `transaction.atomic()` for data integrity

---

## 4. PRODUCT MANAGEMENT

### 4.1 Product Model
**Implementation:** `products/models.py`

**Fields:**
```python
Product:
  - vendor (ForeignKey to CustomUser)
  - name, description
  - price (DecimalField)
  - category (ArrayField - multiple categories)
  - stock (PositiveIntegerField)
  - image (ImageField)
  - is_seasonal (Boolean flag)
  - created_at, updated_at (timestamps)
```

**Categories:**
- Fresh Produce
- Grains and Staples
- Packaged Goods
- Dairy & Eggs
- Meat, Poultry and Seafood
- Local & Specialty Products
- Services

### 4.2 CRUD Operations (Vendor-Only)
**Implementation:** `products/views.py` - Class-Based Views

**Product List View** (`ProductListView`)
- Displays vendor's own products only
- Ordered by creation date (newest first)
- Shows product details and management options

**Create Product** (`ProductCreateView`)
- Form for adding new products
- Multi-category selection support
- Image upload
- Seasonal product toggle
- Stock quantity input
- Form: `ProductForm`

**Update Product** (`ProductUpdateView`)
- Edit existing product information
- Update price, stock, description
- Change categories and images
- Vendor can only edit their own products

**Delete Product** (`ProductDeleteView`)
- Confirmation dialog before deletion
- Soft delete consideration (currently hard delete)
- Vendor can only delete their own products

### 4.3 Access Control (VendorRequiredMixin)
**Implementation:** `products/views.py` - `VendorRequiredMixin`

**Checks:**
1. User must be authenticated
2. User role must be 'VENDOR'
3. Vendor must not be suspended (calls `can_user_add_edit_products()`)
4. Vendor must be verified

**Blocked Scenarios:**
- Unverified vendors
- Suspended vendors (any level)
- Permanently banned vendors
- Consumers attempting to access

### 4.4 Product Display & Discovery
**Implementation:** `products/views.py`, `pages/views.py`

**Home Page Product Display:**
- Shows all products from verified vendors
- Latest products first
- Product cards with image, name, price
- Shop name and verification badge
- Quick "Add to Cart" functionality

**Product Detail API** (`product_detail_api`)
- JSON endpoint for product information
- Returns: name, description, price, stock, category
- Vendor information: shop name, verified status
- Image URL
- Used by modals and AJAX requests

**Product List API** (`product_list_api`)
- Advanced filtering endpoint
- Filters:
  - Text search (name, description)
  - Multiple categories (OR logic)
  - Price range (min/max)
  - Location/region filter (vendor's barangay)
- Returns paginated product list with vendor info

---

## 5. SHOPPING & CART SYSTEM

### 5.1 Shopping Cart (Client-Side)
**Implementation:** JavaScript in `templates/pages/cart.html`, localStorage

**Features:**
- **Add to Cart:**
  - Add products from home page
  - Add from product detail modal
  - Quantity selection
  - Stock validation
  
- **Cart Management:**
  - View all cart items
  - Update quantities
  - Remove items
  - Grouped by vendor/shop
  - Real-time price calculations

- **Cart Persistence:**
  - LocalStorage implementation
  - Persists across sessions
  - Survives page refreshes

### 5.2 Checkout System
**Implementation:** `pages/views.py` - `checkout_api()`

**Process Flow:**
1. **Suspension Check:**
   - Calls `can_user_checkout(user)`
   - Blocks checkout for Level 2+ suspended consumers
   - Returns error message if blocked

2. **Order Processing:**
   - Groups orders by vendor
   - Creates receipt message for each vendor
   - Sends via messaging system

3. **Receipt Details:**
   - Buyer username and contact
   - Item list with quantities and prices
   - Total amount per vendor
   - Timestamp of order

4. **Messaging Integration:**
   - Finds or creates conversation with vendor
   - Sends receipt as message
   - Enables direct communication

5. **Notifications:**
   - **To Consumer:** Order confirmation with item count
   - **To Each Vendor:** New sale notification with details
   - Notification includes link to conversation

**Response:** JSON with success status and redirect URL

---

## 6. SEARCH & DISCOVERY

### 6.1 Product Search
**Implementation:** `pages/views.py` - `search_view()`

**Features:**
- **Search Query:**
  - Text input for product search
  - Searches product name and category
  - Case-insensitive matching
  - Uses Django Q objects (OR logic)

- **Search Results:**
  - Displays matching products
  - Shows product details and vendor info
  - Add to cart from results

- **Search History:**
  - Stores last 5 searches in session
  - Persistent database storage (SearchHistory model)
  - Display recent searches for quick access
  - Click to re-run previous search

### 6.2 Search History Management
**Implementation:** `pages/views.py`, `SearchHistory` model

**Features:**
- **View Recent Searches:**
  - Display last 8 unique searches
  - Ordered by most recent
  - API endpoint: `recent_searches_api()`

- **Delete Individual Search:**
  - Remove specific search term
  - API endpoint: `delete_search_item_api()`
  - AJAX-based deletion

- **Clear All History:**
  - Delete all search records for user
  - Session cleanup
  - API endpoint: `clear_search_history_api()`

**Model:**
```python
SearchHistory:
  - user (ForeignKey)
  - query (search term)
  - searched_at (timestamp)
```

### 6.3 Loyalty Points for Search
**Implementation:** `pages/views.py` - integrated in `search_view()`

**Reward System:**
- **First Search (per unique query):** +5 loyalty points
- **Repeat Search:** No additional points (prevents gaming)
- Automatic LoyaltyProfile creation if doesn't exist
- Updates on each unique search

---

## 7. MESSAGING SYSTEM

### 7.1 Messaging Models
**Implementation:** `messaging/models.py`

**Conversation Model:**
```python
Conversation:
  - participants (ManyToMany to CustomUser)
  - created_at, updated_at
```

**Message Model:**
```python
Message:
  - conversation (ForeignKey)
  - sender (ForeignKey to CustomUser)
  - text_content (TextField)
  - media_file (FileField) - supports images, documents
  - timestamp
  - is_read (Boolean)
  - is_moderator_deleted (Boolean) - soft delete flag
```

**MessageReport Model:**
```python
MessageReport:
  - message (ForeignKey)
  - reporter (ForeignKey)
  - reason (TextField)
  - reported_at (timestamp)
  - is_resolved (Boolean)
  - moderation_action (warn/delete/ban/none)
  - moderator (ForeignKey to admin user)
  - resolution_notes (TextField)
  - resolved_at (timestamp)
```

### 7.2 Inbox & Conversations
**Implementation:** `messaging/views.py` - `inbox_view()`, `conversation_detail_view()`

**Inbox Features:**
- **Conversation List:**
  - Shows all user's conversations
  - Displays other participant's name and avatar
  - Last message preview
  - Unread message count badge
  - Sorted by most recent activity

- **Conversation View:**
  - Two-pane layout: inbox list + chat window
  - Real-time message display
  - Message bubbles (sender vs receiver styling)
  - Timestamp display
  - Media file preview and download

### 7.3 Sending Messages
**Implementation:** `conversation_detail_view()` POST handler

**Features:**
- **Text Messages:**
  - Send text content
  - Empty message validation
  - Character limit enforcement

- **Media Upload:**
  - Upload images, documents
  - File type validation
  - Stored in `media/chat_media/`
  - Display inline or as download link

- **Loyalty Points Reward:**
  - **First message in conversation:** +20 points
  - **Subsequent messages:** +10 points each
  - Encourages vendor-consumer communication

- **Notification:**
  - Recipient gets notification
  - Message: "New message from [username]"
  - Link to conversation

### 7.4 Start Conversation
**Implementation:** `start_conversation_view()`

**Features:**
- Click vendor name or "Message Vendor" button
- Creates new conversation or opens existing one
- Prevents duplicate conversations (checks if 2-person conversation exists)
- Automatic participant addition
- Redirects to conversation detail

### 7.5 Read Status & Notifications
**Implementation:** Integrated in `conversation_detail_view()`

**Features:**
- **Mark as Read:**
  - Messages marked read when conversation opened
  - Only marks messages from other participant
  - Updates is_read flag

- **Notification Cleanup:**
  - Marks conversation notifications as read
  - Clears notification badge count
  - Updates notification dropdown

### 7.6 Message Reporting
**Implementation:** `report_message_view()`

**Features:**
- **Report Button:** On each message in conversation
- **Report Form:**
  - Reason for report (required text)
  - Prevents duplicate reports (same user, same message)
  - Returns error if already reported

- **Report Storage:**
  - Creates MessageReport record
  - Stores reporter, message, reason, timestamp
  - Defaults to unresolved status
  - Admin can review in dashboard

**Response:** JSON with success/error status

---

## 8. NOTIFICATION SYSTEM

### 8.1 Notification Model
**Implementation:** `notifications/models.py`

**Fields:**
```python
Notification:
  - recipient (ForeignKey to CustomUser)
  - message (CharField, 255 max)
  - is_read (Boolean, default=False)
  - timestamp (auto-generated)
  - link (URLField, optional) - where notification leads
```

**Ordering:** Most recent first (`-timestamp`)

### 8.2 Creating Notifications
**Implementation:** `notifications/utils.py` - `create_notification()`

**Usage Pattern:**
```python
create_notification(
    recipient=user_object,
    message="Notification text",
    link="/path/to/relevant/page/"  # optional
)
```

**Triggered By:**
- New message received
- Order placed (buyer and vendor)
- Vendor application approved/denied
- Warning received
- Suspension applied
- Suspension lifted
- Product added (vendor self-notification)
- And more...

### 8.3 Notification Dropdown (Navbar)
**Implementation:** `templates/base.html`, `notifications/views.py` - `recent_notifications_api()`

**Features:**
- **Bell Icon:** Shows unread count badge
- **Dropdown Menu:**
  - 5 most recent notifications
  - Message preview
  - Time since notification (e.g., "5 minutes ago")
  - Read/unread indicator (visual styling)
  - Click to navigate to linked content
  
- **"View All" Link:** Takes to full notification page

**API Response:**
```json
{
  "notifications": [
    {
      "id": 123,
      "message": "New message from John",
      "link": "/messages/5/",
      "is_read": false,
      "time_since": "2 hours ago"
    }
  ],
  "unread_count": 3
}
```

### 8.4 Notification List Page
**Implementation:** `notification_list_view()`, `templates/notifications/notification_list.html`

**Features:**
- Full list of all user notifications
- Paginated display
- Shows message, timestamp, link
- Auto-marks all as read when page visited
- Clickable links to relevant content
- Grouped by read/unread status

---

## 9. LOYALTY REWARDS PROGRAM

### 9.1 Loyalty Profile Model
**Implementation:** `users/models.py`

**Fields:**
```python
LoyaltyProfile:
  - user (OneToOneField to CustomUser)
  - points (PositiveIntegerField, default=0)
  - rank (Bronze/Silver/Gold)
```

**Auto-Creation:** Signal creates profile when user signs up

### 9.2 Earning Points
**Implementation:** Various views with loyalty point integration

**Point Activities:**
- **Search:** +5 points per unique search term
- **First Message (per conversation):** +20 points
- **Subsequent Messages:** +10 points each
- **Product Purchase:** (potential future implementation)
- **Product Review:** (potential future implementation)

### 9.3 Tier System
**Implementation:** `pages/views.py` - `loyalty_rewards()`

**Tiers & Thresholds:**
```
Bronze:    0 - 299 points
Silver:    300 - 1,499 points
Gold:      1,500 - 2,999 points
Platinum:  3,000+ points
```

**Tier Benefits Display:**
- Current tier badge
- Points to next tier
- Progress bar visualization
- Tier benefits list

### 9.4 Rewards Page
**Implementation:** `templates/pages/loyalty_rewards.html`

**Features:**
- **Points Summary:**
  - Current points display
  - Current tier badge
  - Progress to next tier (percentage)
  - Points needed for upgrade

- **Tier Benefits:**
  - List of benefits per tier
  - Unlock status indicators
  - Future reward catalog

- **Points History:**
  - Activity log (potential future feature)
  - Earning breakdown by activity type

### 9.5 Point Deduction (Penalty System)
**Implementation:** `users/suspension_utils.py` - `deduct_loyalty_points()`

**Usage:**
- **1st Suspension (Consumer):** -100 points
- **2nd Suspension (Consumer):** -100 points
- Points cannot go below 0
- Rank auto-updates after deduction
- Used as disciplinary measure

---

## 10. CONTENT MODERATION & SAFETY

### 10.1 Message Reporting System
**Implementation:** `messaging/views.py`, `messaging/models.py`

**User-Side:**
- Report button on each message
- Report form with reason field
- Duplicate report prevention
- Confirmation message after submission

**Admin-Side:** (See Admin Dashboard section)

### 10.2 Warning System
**Implementation:** `CustomUser` model fields

**Fields:**
```python
warning_count (IntegerField):
  - Tracks number of warnings
  - Increments with each warning
  - Resets only by admin action
```

**Warning Threshold:**
- **2 Warnings:** Triggers automatic suspension
- **Warning Messages:** Sent as notifications to user
- Shows warnings remaining before suspension

### 10.3 Moderation Actions
**Implementation:** `dashboard/views.py` - `reported_messages_view()`

**Available Actions:**
1. **Warn:** Send warning to user (triggers suspension at 2 warnings)
2. **Resolve:** Mark report as resolved without action
3. **Delete Message:** Soft delete message (hide from conversation)
4. **Delete Report:** Remove report record entirely
5. **Ban:** Immediate suspension (sets warnings to 2)

**Bulk Actions:**
- Select multiple reports
- Apply action to all selected
- Confirmation dialogs
- Success/error messages

---

## 11. USER SUSPENSION SYSTEM

### 11.1 Suspension Levels & Duration
**Implementation:** `users/suspension_utils.py` - `apply_suspension()`

**Level 1: First Suspension**
- **Duration:** 2 days
- **Trigger:** 2 warnings accumulated
- **Effects:**
  - Account access blocked
  - **Vendors:** Cannot add/edit products
  - **Consumers:** -100 loyalty points
- **Can be lifted:** Automatically after duration

**Level 2: Second Suspension**
- **Duration:** 1 week
- **Effects:**
  - Account access blocked
  - **Vendors:** 
    - Unverified (must reapply)
    - All products deleted
    - Cannot sell until reapproved
  - **Consumers:** 
    - -100 loyalty points
    - Cannot checkout products
- **Can be lifted:** Automatically after duration

**Level 3: Permanent Ban**
- **Duration:** Permanent
- **Trigger:** 3rd suspension
- **Effects:**
  - Account permanently disabled
  - Cannot login
  - All vendor products deleted (if applicable)
  - Cannot be reversed (requires new account)

### 11.2 Suspension Enforcement
**Implementation:** `users/middleware.py` - `SuspensionCheckMiddleware`

**Checks on Every Request:**
1. User authenticated?
2. Check if suspension expired → auto-lift
3. Permanently banned? → Force logout
4. Currently suspended? → Show time remaining, force logout

**Allowed Pages During Suspension:**
- Logout page only
- Displays remaining suspension time

### 11.3 Auto-Lift Mechanism
**Implementation:** `check_and_lift_suspension()`

**Process:**
- Runs on every request (via middleware)
- Compares current time vs. suspension_end_date
- If expired:
  - Sets `is_suspended = False`
  - Clears suspension_end_date
  - Reactivates account (`is_active = True`)
  - Sends "Welcome Back" notification

**Exception:** Permanent bans cannot be auto-lifted

### 11.4 Role-Specific Penalties
**Implementation:** `users/suspension_utils.py`

**Vendor Penalties:**
```python
def unverify_vendor_and_delete_products(user):
    - Sets is_verified = False
    - Deletes all products (Product.objects.filter(vendor=user).delete())
    - Reverts role to 'CONSUMER'
    - Must reapply for vendor status
```

**Consumer Penalties:**
```python
def deduct_loyalty_points(user, points):
    - Deducts specified points (default: 100)
    - Updates loyalty rank
    - Cannot go below 0 points
```

**Checkout Restriction:**
```python
def can_user_checkout(user):
    - Blocks checkout for Level 2+ suspensions
    - Returns False if suspended and suspension_count >= 2
```

**Product Management Restriction:**
```python
def can_user_add_edit_products(user):
    - Checks: is_suspended, is_verified, role
    - Returns False if any check fails
    - Enforced by VendorRequiredMixin
```

### 11.5 Suspension Status Display
**Implementation:** `get_suspension_status_message()`

**Returns Human-Readable Status:**
- "Permanently Banned"
- "Suspended for X more days"
- "Suspended for X more hours"
- "Suspension ending soon"
- "Active (Suspensions: X/3)"

**Used In:**
- Admin dashboard vendor list
- Profile pages
- Admin moderation tools

---

## 12. ADMIN DASHBOARD

### 12.1 Dashboard Overview
**Implementation:** `dashboard/views.py` - `admin_dashboard_view()`

**Statistics Cards:**
- **Total Users:** Count of all registered users
- **Total Vendors:** Users with VENDOR role
- **Total Consumers:** Users with CONSUMER role
- **Total Products:** All products in database
- **Total Product Value:** Sum of all product prices
- **Pending Vendor Applications:** Unverified vendor count
- **Unresolved Reports:** Message reports needing review

**Chart Visualization:**
- **Products Created (7 Days):** Line/bar chart
- Shows daily product creation trend
- Last 7 days of data
- Chart.js implementation

**Recent Activity Table:**
- Latest 5 products added
- Shows: ID, Type, Product Name, Vendor, Date
- Quick overview of platform activity

### 12.2 Vendor Verification Page
**Implementation:** `vendor_verification_view()`

**Two Sections:**

**Pending Applications:**
- Table of unverified vendors
- Columns: Shop Name, Owner, Contact, Region, Applied Date, Actions
- Actions: Approve / Deny buttons
- Inline action with form submission

**Approved Vendors:**
- Table of verified vendors
- Shows verification status
- Product count per vendor
- Shop details

**Actions:**
- **Approve:** 
  - Mark as verified
  - Send notification
  - User can now add products
  
- **Deny:**
  - Delete vendor profile
  - Send notification with reason
  - User can reapply

### 12.3 Reported Messages Management
**Implementation:** `reported_messages_view()`

**Report Table:**
- Columns:
  - Checkbox (for bulk selection)
  - Report ID
  - Reported Message (preview)
  - Sender (reported user)
  - Reason for report
  - Reported By (reporter)
  - Date Reported
  - Status (Resolved/Pending)
  - Suspension Status (of reported user)

**Bulk Action Dropdown:**
- Select multiple reports
- Choose action: Warn / Resolve / Delete Message / Delete Report / Ban
- "Go" button executes action
- Selection counter shows # selected

**Action Implementations:**
1. **Warn:**
   - Increment warning_count
   - Send warning notification
   - At 2 warnings → trigger Level 1 suspension
   - Mark report as resolved

2. **Resolve:**
   - Mark report as resolved
   - No action on reported user
   - Admin note: "Resolved without action"

3. **Delete Message:**
   - Set `is_moderator_deleted = True`
   - Hide message from conversation
   - Notify sender
   - Mark report as resolved

4. **Delete Report:**
   - Permanently delete report record
   - No notification sent

5. **Ban:**
   - Set warnings to 2
   - Immediately trigger suspension
   - Mark report as resolved

**Filtering & Search:**
- Filter by resolved/unresolved
- Search by username
- Sort by date

### 12.4 Vendor Management Page
**Implementation:** `vendor_list_view()`

**Vendor Table:**
- Columns:
  - Checkbox (bulk selection)
  - Shop Name
  - Owner Name
  - Email
  - Region
  - Joined Date
  - Verified Status
  - Product Count
  - Warnings
  - Suspensions (X/3)
  - Current Status

**Bulk Suspension Actions:**
1. **Apply 1st Suspension (2 days):**
   - For vendors with 0 suspensions
   - Sets warnings to 2
   - Applies Level 1 suspension

2. **Apply 2nd Suspension (1 week):**
   - Forces Level 2 suspension
   - Unverifies vendor
   - Deletes all products
   - Must reapply after suspension

3. **Permanent Ban:**
   - Forces Level 3 suspension
   - Account permanently disabled
   - All products deleted
   - **Cannot be undone**

4. **Lift Suspension:**
   - Removes active suspension
   - Restores account access
   - Sends notification
   - Does NOT restore deleted products

5. **Reset Warnings:**
   - Sets warning_count to 0
   - Fresh start for vendor
   - Sends notification

**Search & Filter:**
- Search by shop name, owner name
- Filter by verification status
- Filter by suspension status

### 12.5 Admin Panel Layout
**Implementation:** `dashboard/templates/dashboard/admin_layout_base.html`

**Structure:**
- **Fixed Header:**
  - Admin Panel title
  - User info and logout button
  - Gradient green background
  - Logo/branding

- **Fixed Sidebar:**
  - Navigation menu
  - Links:
    - Dashboard (overview)
    - Vendor Applications
    - Reported Messages
    - Vendor Management
  - Active page highlighting
  - Scrollable if many items

- **Scrollable Content Area:**
  - Main panel content
  - Only content scrolls (header/sidebar fixed)
  - Consistent padding
  - Clean white background

**Responsive Design:**
- Mobile-friendly sidebar collapse
- Touch-friendly buttons
- Responsive tables

---

## 13. UI/UX FEATURES

### 13.1 Responsive Design
**Implementation:** CSS media queries, flexible layouts

**Breakpoints:**
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

**Responsive Elements:**
- Navigation menu (hamburger on mobile)
- Product grid (1/2/3/4 columns)
- Cart layout (stacked on mobile)
- Admin dashboard (sidebar collapse)
- Forms (full-width on mobile)

### 13.2 Color Scheme & Theming
**Implementation:** CSS custom properties in `static/css/theme.css`

**Primary Colors:**
```css
--primary-green: #285429;
--secondary-green: #2e7d32;
--accent-orange: #faa625;
--light-gray: #f9fafb;
--border-gray: #ebebeb;
```

**Theme Consistency:**
- Green for primary actions (agriculture theme)
- Orange for accents and CTAs
- Gray for backgrounds and borders
- White for clean spaces

### 13.3 Typography
**Implementation:** Google Fonts - Noto Sans

**Font Stack:**
```css
font-family: 'Noto Sans', sans-serif;
```

**Weight Usage:**
- 400 (Regular): Body text
- 500 (Medium): Subheadings
- 600 (Semi-Bold): Emphasis
- 700 (Bold): Headings, buttons

### 13.4 Icons & Visual Elements
**Implementation:** Custom SVG icons, Font Awesome (potential)

**Icon Usage:**
- Bell icon for notifications
- Cart icon for shopping
- User avatar placeholders
- Verified badge (checkmark)
- Seasonal product indicator
- Star ratings (future)

### 13.5 Modals & Dialogs
**Implementation:** `static/css/modern_modal.css`, JavaScript

**Product Detail Modal:**
- Click product card → Opens modal
- Product image, name, description
- Price, stock, category
- Vendor information
- Add to cart button
- Close button (X)

**Confirmation Dialogs:**
- Delete product confirmation
- Clear cart confirmation
- Bulk action confirmations
- Logout confirmation

**Features:**
- Backdrop overlay
- Smooth animations (fade in/out)
- Keyboard support (ESC to close)
- Focus trap for accessibility

### 13.6 Loading States & Feedback
**Implementation:** JavaScript, CSS animations

**Loading Indicators:**
- Spinner during AJAX requests
- Button loading state (disabled + spinner)
- Page load animations
- Skeleton screens (potential)

**User Feedback:**
- Success messages (green)
- Error messages (red)
- Warning messages (orange)
- Info messages (blue)
- Toast notifications

### 13.7 Form Validation & UX
**Implementation:** Django form validation, client-side JS validation

**Client-Side:**
- Real-time validation
- Error messages below fields
- Required field indicators (*)
- Input masking (phone, date)
- Character counters (textarea)

**Server-Side:**
- Django form validation
- Custom validators
- Error message display
- Form persistence on error

**UX Enhancements:**
- Placeholder text
- Autofocus on first field
- Tab order optimization
- Submit button state management

### 13.8 Navigation & Menu
**Implementation:** `templates/base.html`, CSS

**Main Navigation:**
- Logo/Home link
- Search bar (expandable on mobile)
- Links: Products, About, Become Vendor
- User dropdown (logged in)
- Login/Signup buttons (logged out)

**User Dropdown:**
- Profile link
- My Products (vendors only)
- Messages
- Notifications
- Loyalty Rewards
- Logout

**Mobile Menu:**
- Hamburger icon toggle
- Slide-out drawer
- Full-screen overlay
- Smooth animations

### 13.9 Product Cards & Grid
**Implementation:** `templates/pages/home.html`, CSS Grid/Flexbox

**Product Card Elements:**
- Product image (with fallback)
- Product name
- Price (formatted ₱X,XXX.XX)
- Shop name
- Verified badge (if applicable)
- Seasonal indicator (if applicable)
- Add to cart button
- Quick view button

**Grid Layout:**
- 4 columns on desktop
- 3 columns on tablet
- 2 columns on mobile
- Gap spacing: 1.5rem
- Responsive images

### 13.10 Accessibility Features
**Implementation:** Semantic HTML, ARIA attributes

**Features:**
- Semantic HTML5 tags (nav, main, article, aside)
- ARIA labels for interactive elements
- Keyboard navigation support
- Focus indicators (visible outlines)
- Alt text for images
- Screen reader friendly
- Color contrast compliance (WCAG AA)

### 13.11 Performance Optimizations
**Implementation:** Django optimization, CSS/JS minification

**Backend:**
- Database query optimization
  - `select_related()` for foreign keys
  - `prefetch_related()` for many-to-many
  - Indexing on frequently queried fields
- Pagination for long lists
- Lazy loading for images

**Frontend:**
- CSS minification
- JavaScript minification
- Image compression
- LocalStorage for cart (no DB hits)
- AJAX for dynamic content (no page reload)

### 13.12 Error Handling & 404 Pages
**Implementation:** Django error views, custom templates

**Error Pages:**
- 404 Not Found (custom template)
- 403 Forbidden (permission denied)
- 500 Server Error (graceful degradation)
- Custom error messages

**User-Friendly:**
- Clear error explanations
- Links to return home
- Contact information
- Search functionality on 404

---

## 🔧 TECHNICAL IMPLEMENTATION DETAILS

### Database Schema
**Tables:**
- `users_customuser` (extends Django AbstractUser)
- `users_vendorprofile` (one-to-one with CustomUser)
- `users_loyaltyprofile` (one-to-one with CustomUser)
- `users_searchhistory`
- `products_product`
- `messaging_conversation`
- `messaging_message`
- `messaging_messagereport`
- `notifications_notification`

### Middleware
1. **SecurityMiddleware** (Django default)
2. **WhiteNoiseMiddleware** (static file serving)
3. **SessionMiddleware** (Django default)
4. **CommonMiddleware** (Django default)
5. **CsrfViewMiddleware** (CSRF protection)
6. **AuthenticationMiddleware** (Django default)
7. **SuspensionCheckMiddleware** (custom - checks user suspension)
8. **MessageMiddleware** (Django messages framework)

### URL Patterns
```
/ - Home page
/about/ - About page
/login/ - Login
/signup/ - Consumer signup
/vendor-signup/ - Vendor signup
/logout/ - Logout
/profile/ - Consumer profile
/vendor-profile/ - Vendor profile
/become-vendor/ - Vendor onboarding start
/vendor-onboarding/step1/ - Shop info
/vendor-onboarding/step2/ - Personal details
/vendor-onboarding/step3/ - Review
/vendor-onboarding/success/ - Success page
/my-products/ - Vendor product list
/products/add/ - Add product
/products/<id>/edit/ - Edit product
/products/<id>/delete/ - Delete product
/cart/ - Shopping cart
/search/ - Product search
/loyalty-rewards/ - Loyalty page
/messages/ - Inbox
/messages/<conversation_id>/ - Conversation
/messages/start/<recipient_id>/ - Start conversation
/notifications/ - Notification list
/admin-dashboard/ - Admin dashboard
/admin/vendor-verification/ - Vendor applications
/admin/reported-messages/ - Message reports
/admin/vendor-list/ - Vendor management
```

### API Endpoints
```
/api/product/<id>/ - Product detail JSON
/api/products/ - Product list with filters
/api/vendor/<id>/ - Vendor detail JSON
/api/checkout/ - Process checkout
/api/recent-searches/ - Search history
/api/delete-search/ - Delete search item
/api/clear-searches/ - Clear all searches
/api/recent-notifications/ - Notification dropdown
/api/report-message/<id>/ - Report message
```

---

## 📊 KEY METRICS & ANALYTICS (Potential)

### User Engagement
- Daily active users
- Average session duration
- Messages sent per day
- Products viewed per session
- Search queries per day

### Business Metrics
- Total transactions (orders placed)
- Average order value
- Vendor signup rate
- Vendor verification rate
- Product listing rate

### Platform Health
- Message reports per day
- Warnings issued
- Suspensions active
- Permanent bans total
- Average response time (admin to reports)

---

## 🚀 FUTURE ENHANCEMENTS (Potential)

### Phase 2 Features
1. **Payment Integration:** Actual checkout with payment gateway
2. **Order Tracking:** Track order status from placement to delivery
3. **Ratings & Reviews:** Product and vendor reviews
4. **Advanced Search:** Filters for price, rating, distance
5. **Map Integration:** Show vendor locations on map
6. **Mobile App:** Native iOS/Android apps
7. **SMS Notifications:** Text message alerts for orders
8. **Email System:** Order confirmations via email
9. **Analytics Dashboard:** Vendor sales analytics
10. **Inventory Management:** Auto stock updates on checkout

### Phase 3 Features
1. **AI Recommendations:** Personalized product suggestions
2. **Seasonal Alerts:** Notify when favorite products in season
3. **Bulk Orders:** B2B ordering for restaurants
4. **Subscription Boxes:** Weekly produce delivery
5. **Community Forum:** Discussion board for farmers/consumers
6. **Video Chat:** Live vendor consultations
7. **Recipe Integration:** Recipes using available products
8. **Carbon Footprint:** Show environmental impact of purchases

---

## 📝 TESTING CHECKLIST

### Functional Testing
- [ ] User registration (consumer and vendor)
- [ ] Login/logout functionality
- [ ] Profile updates (with image upload)
- [ ] Vendor onboarding (3-step process)
- [ ] Product CRUD operations
- [ ] Add to cart and checkout
- [ ] Search functionality
- [ ] Messaging (text and media)
- [ ] Notification system
- [ ] Loyalty points earning
- [ ] Report message feature
- [ ] Admin dashboard statistics
- [ ] Vendor verification approval/denial
- [ ] Bulk moderation actions
- [ ] Suspension system (all 3 levels)
- [ ] Auto-lift suspension

### Security Testing
- [ ] CSRF protection on forms
- [ ] SQL injection prevention
- [ ] XSS vulnerability checks
- [ ] Authentication required for protected views
- [ ] Role-based access control
- [ ] File upload validation
- [ ] Suspension enforcement

### Performance Testing
- [ ] Page load times < 3 seconds
- [ ] Database query optimization
- [ ] Image loading performance
- [ ] Cart operations (localStorage)
- [ ] Search response time

### Usability Testing
- [ ] Mobile responsiveness
- [ ] Form error handling
- [ ] Loading states display
- [ ] Success/error message clarity
- [ ] Navigation intuitiveness
- [ ] Accessibility compliance

---

## 🎓 PRESENTATION TIPS

### Key Selling Points
1. **Direct Farm-to-Consumer:** Eliminates middlemen, better prices for both parties
2. **Vendor Verification:** Builds trust, ensures legitimate businesses
3. **Comprehensive Moderation:** Keeps platform safe and professional
4. **Loyalty Program:** Encourages repeat usage and engagement
5. **Seamless Communication:** Built-in messaging for easy coordination
6. **Progressive Discipline:** Fair 3-level suspension system with role-specific penalties
7. **Admin Tools:** Powerful dashboard for platform management
8. **Responsive Design:** Works on all devices

### Demo Flow Suggestion
1. **Start:** Show home page with products
2. **Consumer Journey:**
   - Register as consumer
   - Search for product
   - View product details
   - Add to cart
   - Checkout (show receipt in messages)
   - Check notifications and loyalty points

3. **Vendor Journey:**
   - Register as vendor
   - Complete 3-step onboarding
   - Show pending status
   - (Switch to admin) Approve vendor
   - (Back to vendor) Add product
   - View product in marketplace

4. **Admin Journey:**
   - Show dashboard statistics
   - Review vendor applications
   - Handle message reports
   - Apply suspension
   - Show suspended user blocked from actions

5. **Moderation Demo:**
   - Report a message
   - (Admin) Apply warning → show suspension trigger
   - Show suspended user notifications
   - Demonstrate role-specific penalties

### Technical Highlights
- Django Framework: Industry-standard, scalable
- PostgreSQL: Robust relational database
- RESTful APIs: Modern architecture
- Middleware: Custom suspension enforcement
- Signal Handlers: Automatic profile creation
- Transaction Management: Data integrity
- Security: CSRF, authentication, authorization

---

## 📞 SUPPORT & DOCUMENTATION

**Repository:** GitHub (morel-porel/CSIT327-G1-Sari-SariAgriculturalMarket)  
**Database:** PostgreSQL on Supabase  
**Environment:** Python 3.x, Django 5.2.6  
**Additional Docs:** SUSPENSION_SYSTEM_GUIDE.md

---

**Last Updated:** December 3, 2025  
**Version:** 1.0 (Production Ready)  
**Team:** CSIT327 Group 1
