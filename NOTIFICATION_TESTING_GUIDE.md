# Notification System Testing Guide

## Quick Start Testing

### 1. Access the Application

The application is currently running at: **http://localhost:8000**

### 2. Test Notification Dropdown

**Steps:**

1. Log in as any user (intern, supervisor, manager, or admin)
2. Look at the top-right navbar - you should see a bell icon 🔔
3. The bell should have a badge if there are unread notifications
4. Click the bell to open the dropdown
5. You should see recent notifications (up to 5)

**Expected Behavior:**

- Bell icon visible in navbar
- Badge shows unread count
- Dropdown shows recent notifications with icons
- "Mark all read" button available
- "View All Notifications" link available

---

### 3. Test Notification Center

**Steps:**

1. Click "View All Notifications" from the dropdown OR
2. Navigate to: `http://localhost:8000/notifications/`

**Expected Behavior:**

- Full list of all notifications
- Filter by status (All, Unread, Read)
- Filter by category (Attendance, Assessment, Absenteeism, etc.)
- Unread notifications have blue left border and "New" badge
- Clicking a notification marks it as read and navigates to action page

---

### 4. Test Mark as Read

**Steps:**

1. Find an unread notification (blue border, "New" badge)
2. Click on the notification

**Expected Behavior:**

- Notification is marked as read
- Badge count decreases
- Blue border and "New" badge removed
- Redirects to relevant page (if action_url exists)

---

### 5. Test Mark All as Read

**Steps:**

1. Go to notification center
2. Click "Mark All as Read" button

**Expected Behavior:**

- All notifications marked as read
- Badge count becomes 0
- Success message displayed
- Page refreshes showing all as read

---

### 6. Test Notification Preferences

**Steps:**

1. Click user dropdown (top-right)
2. Click "Notification Settings" OR
3. Navigate to: `http://localhost:8000/notifications/preferences/`

**Expected Behavior:**

- Form with toggle switches
- In-app notifications toggle
- Email notifications toggle
- When email enabled, category-specific toggles appear
- Email frequency radio buttons (Instant, Daily, Weekly)
- Save button updates preferences

---

### 7. Test Notification Creation

#### Method A: Via Django Admin

1. Navigate to: `http://localhost:8000/admin/`
2. Log in as admin
3. Go to "Notifications" → "Notifications"
4. Click "Add Notification"
5. Fill in:
   - **User**: Select a user
   - **Title**: "Test Notification"
   - **Message**: "This is a test notification"
   - **Notification type**: Info/Success/Warning/Error
   - **Category**: Any category
6. Save
7. Log in as that user
8. Check if notification appears in dropdown

#### Method B: Via Real Actions

**Test Attendance Approval Notification:**

1. Log in as an intern
2. Submit attendance (if not already done)
3. Log out
4. Log in as supervisor/manager
5. Go to "Pending Approvals"
6. Approve or reject attendance
7. Log out
8. Log in as the intern
9. Check notification dropdown - should see attendance notification

**Test Assessment Notification:**

1. Log in as supervisor/manager
2. Go to "Assessments" → "Assessment List"
3. Create new assessment for an intern
4. Log out
5. Log in as that intern
6. Check notification dropdown - should see assessment notification

**Test Absence Approval Notification:**

1. Log in as intern
2. Submit absence request (if not already done)
3. Log out
4. Log in as supervisor/manager
5. Go to "Absence Requests"
6. Approve or reject absence
7. Log out
8. Log in as intern
9. Check notification dropdown - should see absence notification

---

## Expected Notification Flows

### 1. Attendance Approved

**Trigger**: Supervisor/Manager approves attendance  
**Recipient**: Intern  
**Type**: Success (green checkmark icon)  
**Category**: Attendance  
**Title**: "Attendance Approved"  
**Message**: "Your attendance for [date] has been approved by [approver]"  
**Action URL**: Link to attendance detail

### 2. Attendance Rejected

**Trigger**: Supervisor/Manager rejects attendance  
**Recipient**: Intern  
**Type**: Warning (orange triangle icon)  
**Category**: Attendance  
**Title**: "Attendance Rejected"  
**Message**: "Your attendance for [date] was rejected by [approver]. Reason: [reason]"  
**Action URL**: Link to attendance detail

### 3. Assessment Created

**Trigger**: Supervisor creates assessment  
**Recipient**: Intern  
**Type**: Info (blue info icon)  
**Category**: Assessment  
**Title**: "New Assessment Available"  
**Message**: "A new assessment (Week [number]) has been created by [creator]"  
**Action URL**: Link to assessment view

### 4. Assessment Reviewed

**Trigger**: Supervisor completes assessment  
**Recipient**: Intern  
**Type**: Success (green checkmark icon)  
**Category**: Assessment  
**Title**: "Assessment Completed"  
**Message**: "Your Week [number] assessment has been completed by [reviewer]"  
**Action URL**: Link to assessment view

### 5. Absence Approved

**Trigger**: Supervisor/Manager approves absence  
**Recipient**: Intern  
**Type**: Success (green checkmark icon)  
**Category**: Absenteeism  
**Title**: "Absence Request Approved"  
**Message**: "Your absence request for [date range] has been approved by [approver]"  
**Action URL**: Link to absence detail

### 6. Absence Rejected

**Trigger**: Supervisor/Manager rejects absence  
**Recipient**: Intern  
**Type**: Warning (orange triangle icon)  
**Category**: Absenteeism  
**Title**: "Absence Request Rejected"  
**Message**: "Your absence request for [date range] was rejected by [approver]. Reason: [reason]"  
**Action URL**: Link to absence detail

---

## Troubleshooting

### Issue: No bell icon in navbar

**Solution**:

- Clear browser cache
- Check that user is logged in
- Verify context processor is registered in settings

### Issue: Badge count shows 0 but there are unread notifications

**Solution**:

- Refresh the page
- Check database: `docker-compose exec web python manage.py shell`
  ```python
  from apps.notifications.models import Notification
  Notification.objects.filter(user__username='<username>', is_read=False).count()
  ```

### Issue: Notifications not being created

**Solution**:

1. Check Docker logs: `docker-compose logs web`
2. Verify NotificationService import in views
3. Check that user has email address (required for email notifications)
4. Test notification creation manually in Django shell

### Issue: Dropdown not showing notifications

**Solution**:

- Check browser console for JavaScript errors
- Verify Bootstrap CSS/JS are loaded
- Check that `recent_notifications` is in context

### Issue: Email notifications not sending

**Solution**:

- Email backend not configured yet (see NOTIFICATION_SYSTEM_IMPLEMENTATION.md)
- Configure SMTP settings in `config/settings.py`
- For testing, use console backend: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

---

## Database Verification Commands

### Check notifications for a user

```bash
docker-compose exec web python manage.py shell
```

```python
from apps.notifications.models import Notification
from apps.accounts.models import User

# Get user
user = User.objects.get(username='intern_user')  # Change username

# Count notifications
total = Notification.objects.filter(user=user).count()
unread = Notification.objects.filter(user=user, is_read=False).count()

print(f"Total notifications: {total}")
print(f"Unread notifications: {unread}")

# List recent notifications
for notif in Notification.objects.filter(user=user).order_by('-created_at')[:5]:
    print(f"- [{notif.notification_type}] {notif.title}: {notif.message}")
```

### Create test notification

```bash
docker-compose exec web python manage.py shell
```

```python
from apps.notifications.models import Notification
from apps.accounts.models import User

# Get user
user = User.objects.first()  # Or get specific user

# Create notification
Notification.objects.create(
    user=user,
    title="Test Notification",
    message="This is a test notification created via shell",
    notification_type="info",
    category="system"
)

print(f"Notification created for {user.username}")
```

---

## Success Criteria

✅ **All tests pass if:**

1. Bell icon visible in navbar for all logged-in users
2. Badge shows correct unread count
3. Dropdown displays recent notifications
4. Notification center shows all notifications
5. Filters work correctly (status, category)
6. Mark as read functionality works
7. Mark all as read functionality works
8. Preferences page loads and saves correctly
9. Real actions (approval/rejection) create notifications
10. Notifications appear immediately after creation (after page refresh)

---

## Current Testing Status

- ✅ Application running: http://localhost:8000
- ✅ Django system check: No errors
- ✅ Docker containers: Running
- ⏳ Manual testing: Pending user verification

**Ready for testing!** Please follow the steps above and report any issues.
