# Supervisor Absence Request Notification Feature

**Date:** October 14, 2025  
**Status:** ✅ IMPLEMENTED

---

## Summary

**Before:** Supervisors were NOT notified when interns submitted absence requests  
**After:** Supervisors now receive in-app AND email notifications when interns submit absence requests

---

## Complete Notification Flow

### 1. **Intern Submits Absence Request** → Supervisor Notified ✅ (NEW)

- **Trigger:** Intern submits new absence request
- **Recipient:** Intern's supervisor
- **Type:** Info (blue icon)
- **Category:** Absenteeism
- **Title:** "New Absence Request Pending Approval"
- **Message:** "[Intern Name] submitted an absence request for [date range]. Reason: [reason]"
- **Action URL:** Link to pending requests page
- **Email:** YES (sent to supervisor)

### 2. **Supervisor Approves Absence Request** → Intern Notified ✅

- **Trigger:** Supervisor approves absence request
- **Recipient:** Intern who submitted the request
- **Type:** Success (green checkmark)
- **Category:** Absenteeism
- **Title:** "Absence Request Approved ✓"
- **Message:** "Your absence request for [date range] has been approved by [Approver Name]"
- **Action URL:** Link to "My Requests" page
- **Email:** YES (sent to intern)

### 3. **Supervisor Rejects Absence Request** → Intern Notified ✅

- **Trigger:** Supervisor rejects absence request
- **Recipient:** Intern who submitted the request
- **Type:** Error (red X icon)
- **Category:** Absenteeism
- **Title:** "Absence Request Rejected"
- **Message:** "Your absence request for [date range] was rejected by [Approver Name]. Reason: [rejection reason]"
- **Action URL:** Link to "My Requests" page
- **Email:** YES (sent to intern)

---

## Implementation Details

### 1. Added New Notification Method

**File:** `apps/notifications/services.py`

```python
@staticmethod
def notify_supervisor_new_absence_request(absence_request):
    """Notify supervisor of new absence request from intern"""
    if absence_request.intern.internal_supervisor:
        NotificationService.create_notification(
            recipient=absence_request.intern.internal_supervisor.user,
            title="New Absence Request Pending Approval",
            message=f"{absence_request.intern.user.get_full_name()} submitted an absence request for {absence_request.start_date} to {absence_request.end_date}. Reason: {absence_request.reason}",
            notification_type="info",
            category="absenteeism",
            action_url=reverse("absenteeism:pending_requests"),
            related_object=absence_request,
            send_email=True,  # Email supervisors about new absence requests
        )
```

### 2. Wired Notification into View

**File:** `apps/absenteeism/views.py`

```python
@login_required
@intern_required
def request_absence(request):
    """Intern submits absenteeism request"""
    intern_profile = get_object_or_404(InternProfile, user=request.user)

    if request.method == "POST":
        form = AbsenteeismRequestForm(request.POST, request.FILES)
        if form.is_valid():
            absence_request = form.save(commit=False)
            absence_request.intern = intern_profile
            absence_request.save()

            # Notify supervisor of new absence request
            NotificationService.notify_supervisor_new_absence_request(absence_request)

            messages.success(
                request,
                "Your absence request has been submitted successfully and is pending approval.",
            )
            return redirect("absenteeism:my_requests")
```

---

## Comparison with Similar Features

### Attendance Notifications

- **Intern submits attendance** → Supervisor notified (in-app only, no email)
- **Supervisor approves/rejects** → Intern notified (in-app + email)

### Absence Notifications (NOW COMPLETE)

- **Intern submits absence request** → Supervisor notified (in-app + email) ✅ **NEW**
- **Supervisor approves/rejects** → Intern notified (in-app + email) ✅

### Assessment Notifications

- **Supervisor creates assessment** → Intern notified (in-app + email)
- **Intern completes self-assessment** → Supervisor notified (in-app + email)
- **Supervisor reviews assessment** → Intern notified (in-app + email)

---

## Why Supervisors Get Email for Absence Requests

**Design Decision:** `send_email=True` for absence requests

**Reasoning:**

- Absence requests are **more important** than routine attendance
- Require **timely approval** (intern may need to be absent soon)
- May involve **documentation review** (sick notes, certificates)
- Lower frequency than daily attendance (less email noise)

**Different from Attendance:**

- Attendance notifications: `send_email=False` (too frequent)
- Absence notifications: `send_email=True` (important & infrequent)

---

## How to Test

### Test 1: Intern Submits Absence Request

1. **Log in as intern**
2. Navigate to "Absence Requests" → "Request Absence"
3. Fill out the form:
   - Start date
   - End date
   - Reason
   - Supporting document (optional)
4. Click "Submit Request"
5. **Expected:** Success message shown

6. **Log out and log in as supervisor**
7. Check notification bell (🔔) in navbar
8. **Expected:**
   - Badge shows "1" (or increased count)
   - Dropdown shows new notification:
     - Title: "New Absence Request Pending Approval"
     - Message: "[Intern Name] submitted an absence request for [dates]. Reason: [reason]"
     - Blue info icon
   - Clicking notification redirects to pending requests page

### Test 2: Supervisor Approves Absence Request

1. **While logged in as supervisor**
2. Go to "Absence Requests" → "Pending Requests"
3. Click "Approve" on the absence request
4. Add optional note
5. Click "Approve"

6. **Log out and log in as intern**
7. Check notification bell
8. **Expected:**
   - New notification: "Absence Request Approved ✓"
   - Green success icon
   - Message includes supervisor name

### Test 3: Supervisor Rejects Absence Request

1. **While logged in as supervisor**
2. Go to "Absence Requests" → "Pending Requests"
3. Click "Reject" on the absence request
4. Add rejection reason
5. Click "Reject"

6. **Log out and log in as intern**
7. Check notification bell
8. **Expected:**
   - New notification: "Absence Request Rejected"
   - Red error icon
   - Message includes supervisor name and rejection reason

---

## Email Notification Preview

**Subject:** [IMS] New Absence Request Pending Approval

**Body:**

```
Hi [Supervisor Name],

[Intern Name] submitted an absence request for [start_date] to [end_date].

Reason: [absence reason]

Please review and approve or reject this request.

View Pending Requests: [link]

---
Internship Management System
```

---

## Impact

### Benefits:

✅ **Supervisors notified immediately** when interns submit absence requests  
✅ **Email notification** ensures supervisors don't miss important requests  
✅ **Consistent** with other notification workflows  
✅ **Timely approvals** - supervisors can respond quickly  
✅ **Better communication** between interns and supervisors

### User Experience:

- Supervisors no longer need to manually check for pending absence requests
- Interns get confirmation their request was received
- Clear audit trail of all absence-related communications

---

## Status

🟢 **Feature fully implemented and tested**

**Notification System Coverage:**

- ✅ Attendance (submit → notify supervisor, approve/reject → notify intern)
- ✅ Absence (submit → notify supervisor, approve/reject → notify intern) **COMPLETE**
- ✅ Assessment (create/review → notify intern, self-assess → notify supervisor)
- ✅ Preferences page (all user roles can save settings)

**Next:** Continue comprehensive testing of all notification flows.
