# Dashboard Testing Guide

## Overview

This guide will help you test the Internship Management System dashboards at the UI level. All dashboards now display real data from the database.

## System Access

### 1. Start the System

```bash
docker-compose up -d
```

### 2. Access the Web Interface

Open your browser and navigate to: **http://localhost:8000**

## Test User Accounts

### Intern User

- **Username:** `intern1`
- **Password:** `intern123`
- **Role:** Intern
- **Dashboard Features:**
  - View approved attendance count
  - See reviewed assessments with average scores
  - Track approved absence requests
  - View recent assessments (last 3)
  - View recent absence requests (last 3)
  - Quick check-in button
  - Quick assessment access

### Supervisor User

- **Username:** `supervisor1`
- **Password:** `supervisor123`
- **Role:** Internal Supervisor
- **Dashboard Features:**
  - View pending attendance approvals
  - See pending assessments awaiting review
  - Manage pending absence requests
  - View list of assigned interns
  - Quick approve/review buttons
  - Access intern assessment forms

### Admin User

- **Username:** `admin`
- **Password:** `admin123`
- **Role:** System Administrator
- **Dashboard Features:**
  - View system-wide statistics
  - Total users, interns, supervisors
  - All pending items across system
  - Recent user registrations
  - Recent system activity
  - User management access

### Manager User

- **Username:** `manager1`
- **Password:** `manager123`
- **Role:** Manager
- **Dashboard Features:**
  - System-wide overview
  - All pending approvals
  - Active intern statistics
  - Recent activity logs
  - Branch and supervisor management

## Testing Checklist

### Intern Dashboard Testing

- [ ] **Statistics Display**

  - [ ] Approved attendance count shows correct number
  - [ ] Reviewed assessments count displays properly
  - [ ] Average score displays with correct color (green/yellow/red)
  - [ ] Approved absence requests count is accurate

- [ ] **Attendance Section**

  - [ ] Total attendance count is correct
  - [ ] Approved/pending/rejected counts match records
  - [ ] "View All" button navigates to attendance list
  - [ ] Check-in button is functional

- [ ] **Assessment Section**

  - [ ] Total assessments count is correct
  - [ ] Pending/reviewed counts are accurate
  - [ ] Average supervisor score displays correctly
  - [ ] Recent assessments list shows last 3 items
  - [ ] Each assessment has correct status badge
  - [ ] Assessment links navigate properly
  - [ ] "View All" button works
  - [ ] Empty state displays when no assessments exist

- [ ] **Absence Requests Section**
  - [ ] Total absence requests count is correct
  - [ ] Pending/approved counts are accurate
  - [ ] Recent absence requests list shows last 3 items
  - [ ] Each request has correct status badge
  - [ ] Request links navigate properly
  - [ ] "View All" button works
  - [ ] Empty state displays when no requests exist

### Supervisor Dashboard Testing

- [ ] **Pending Attendance Section**

  - [ ] Shows count of pending attendance records
  - [ ] Displays recent 5 pending items
  - [ ] Shows intern name and date for each
  - [ ] Quick approve links work
  - [ ] "View All" button navigates correctly
  - [ ] Empty state displays when no pending items

- [ ] **Pending Assessments Section**

  - [ ] Shows count of pending assessments
  - [ ] Displays recent 5 assessments awaiting review
  - [ ] Shows intern name and assessment type
  - [ ] Review links navigate correctly
  - [ ] "View All" button works
  - [ ] Empty state displays appropriately

- [ ] **Pending Absence Requests Section**

  - [ ] Shows count of pending requests
  - [ ] Displays recent 5 pending absence requests
  - [ ] Shows intern name and date range
  - [ ] Approval links work
  - [ ] "View All" button navigates correctly
  - [ ] Empty state displays when no requests

- [ ] **My Interns Section**
  - [ ] Table shows only interns assigned to this supervisor
  - [ ] Displays intern name, email, school, branch
  - [ ] Quick assess button works for each intern
  - [ ] Empty state if no assigned interns

### Manager Dashboard Testing

- [ ] **System Statistics**

  - [ ] Total interns count is correct
  - [ ] Total supervisors count is accurate
  - [ ] Total branches count displays properly
  - [ ] Total assessments count is correct
  - [ ] Pending counts match actual records
  - [ ] Active interns (last 7 days) is accurate

- [ ] **Recent Activity**
  - [ ] Shows last 10 system activities
  - [ ] Activities display in chronological order
  - [ ] Quick links navigate correctly

### Admin Dashboard Testing

- [ ] **System Overview**

  - [ ] Total users count is correct
  - [ ] Total interns count matches database
  - [ ] Total supervisors count is accurate
  - [ ] Total branches and schools counts are correct
  - [ ] All activity counts (attendance, assessments, absences) are accurate

- [ ] **Active Sessions**

  - [ ] Shows users active in last 24 hours
  - [ ] Count matches actual active sessions

- [ ] **Recent Users**

  - [ ] Displays last 5 registered users
  - [ ] User information is accurate

- [ ] **Recent Activity**
  - [ ] Shows last 10 system-wide activities
  - [ ] Links navigate correctly

## Common Issues and Troubleshooting

### Dashboard Shows No Data

**Problem:** Statistics show zeros or "No items yet"
**Solution:**

1. Ensure you're logged in as the correct user type
2. Verify test data exists in database:
   ```bash
   docker-compose exec web python manage.py shell
   >>> from apps.attendance.models import Attendance
   >>> Attendance.objects.count()
   ```

### Links Don't Navigate

**Problem:** Clicking "View All" or item links does nothing
**Solution:**

1. Check browser console for JavaScript errors
2. Verify URL patterns are configured in `urls.py`
3. Ensure user has permission to access target page

### Container Not Running

**Problem:** Cannot access http://localhost:8000
**Solution:**

```bash
# Check container status
docker-compose ps

# Restart containers
docker-compose restart

# View logs
docker-compose logs web
```

### Database Connection Issues

**Problem:** "Connection refused" or database errors
**Solution:**

```bash
# Restart database container
docker-compose restart db

# Wait 10 seconds for database to initialize
sleep 10

# Restart web container
docker-compose restart web
```

## Next Steps After Testing

Once you've verified the dashboards work correctly:

1. **Report Issues**: Document any bugs or missing features
2. **Request Enhancements**: Identify additional dashboard features needed
3. **Continue Development**: Move to next system components:
   - Notification system
   - PDF report generation
   - Activity logging
   - Admin configuration interface

## Testing Data

If you need to create additional test data:

```bash
# Access Django shell
docker-compose exec web python manage.py shell

# Create test attendance
from apps.attendance.models import Attendance
from apps.interns.models import InternProfile
from django.utils import timezone

intern = InternProfile.objects.first()
Attendance.objects.create(
    intern=intern,
    date=timezone.now().date(),
    status='pending'
)

# Create test assessment
from apps.evaluations.models import PerformanceAssessment

PerformanceAssessment.objects.create(
    intern=intern,
    assessment_type='supervisor',
    submitted_by=intern.internal_supervisor,
    overall_score=85
)

# Create test absence request
from apps.absenteeism.models import AbsenteeismRequest

AbsenteeismRequest.objects.create(
    intern=intern,
    start_date=timezone.now().date(),
    end_date=timezone.now().date() + timezone.timedelta(days=1),
    reason='Medical appointment',
    status='pending'
)
```

## Support

If you encounter issues during testing:

1. Check the container logs: `docker-compose logs web`
2. Verify database connection: `docker-compose logs db`
3. Review Django debug output in browser (DEBUG=True in development)
4. Check this guide's troubleshooting section

---

**Happy Testing! 🚀**
