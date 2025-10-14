# TODO: Pending Features & Improvements

This document lists all features that have been identified but not yet implemented in the Internship Management System.

**Last Updated:** October 14, 2025

---

## 🔴 High Priority

### 1. Email Configuration

**Status:** Not Implemented  
**Current State:** Email settings exist but not configured  
**What's Missing:**

- Configure SMTP settings in `config/settings.py`
- Set up email backend (Gmail, SendGrid, AWS SES, etc.)
- Test email sending functionality
- Configure email templates styling

**Files to Modify:**

- `config/settings.py` - Add EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, etc.
- Environment variables for email credentials

**Impact:** Notifications are created but not sent via email

---

### 2. ActivityLog User Interface

**Status:** Model exists, no UI  
**Current State:** `apps/log/models.py` has ActivityLog model  
**What's Missing:**

- View to display activity logs
- Template for activity log listing
- Filtering by user, action type, date range
- Export logs to CSV
- Admin interface for log management

**Files to Create:**

- `apps/log/views.py` - Add list_logs view
- `templates/log/activity_log.html` - Activity log listing page
- `apps/log/urls.py` - URL patterns for log views

**Related Models:**

- `ActivityLog` in `apps/log/models.py`

---

### 3. Profile Picture Upload & Display

**Status:** Field exists, no implementation  
**Current State:** User model may have profile picture field  
**What's Missing:**

- Image upload in profile form
- Image validation (size, format)
- Image preview before upload
- Display profile pictures in navbar
- Display in user lists
- Image compression/optimization
- Default avatar fallback

**Files to Modify:**

- `apps/accounts/forms.py` - Add profile_picture to UserProfileForm
- `templates/accounts/profile.html` - Add image upload widget
- `templates/dashboards/base.html` - Display profile picture in navbar
- `config/settings.py` - Configure MEDIA_ROOT and MEDIA_URL

**Additional Setup:**

- Install Pillow for image processing: `pip install Pillow`
- Configure media file serving in development and production

---

### 4. Emergency Contact Information Collection

**Status:** Fields exist, no form  
**Current State:** Models likely have emergency contact fields  
**What's Missing:**

- Form to collect emergency contact info
- Display emergency contacts in profile
- Edit emergency contact information
- Emergency contact listing for supervisors/managers

**Files to Create/Modify:**

- `apps/interns/forms.py` - EmergencyContactForm
- `templates/interns/emergency_contact.html`
- `apps/interns/views.py` - Add emergency contact views

**Related Models:**

- Check `InternProfile` or related models for emergency contact fields

---

## 🟡 Medium Priority

### 5. Application Portal for Potential Interns

**Status:** Not Implemented (User declined during discussion)  
**Current State:** N/A  
**What's Needed:**

- Public-facing application form
- File upload for CV/resume and cover letter
- Application status tracking
- Admin review interface
- Email notifications for applicants
- Application deadline management

**Implementation Scope:**

- New app: `apps/applications/`
- Public URLs (no login required)
- Admin approval workflow
- Automatic account creation upon approval

**Note:** User preferred to handle this manually for now

---

### 6. Document Preview for Absence Requests

**Status:** Upload exists, no preview  
**Current State:** Can upload supporting documents  
**What's Missing:**

- Preview uploaded documents (PDF, images)
- Download documents
- Document thumbnail generation
- File type validation
- Virus scanning (optional)

**Files to Modify:**

- `templates/absenteeism/detail.html` - Add preview modal
- Add PDF.js or similar for PDF preview
- Image preview with lightbox

---

### 7. Search & Filtering Features

**Status:** Basic lists exist, limited filtering  
**What's Missing:**

#### Attendance Search/Filter:

- Filter by date range
- Filter by approval status
- Filter by branch
- Filter by intern
- Export filtered results

#### Assessment Search/Filter:

- Filter by date range
- Filter by score range
- Filter by intern
- Filter by supervisor
- Search by comments

#### Intern Search/Filter:

- Search by name, email
- Filter by branch
- Filter by school
- Filter by internship status
- Advanced search options

**Files to Modify:**

- `apps/attendance/views.py` - Add filtering logic
- `apps/evaluations/views.py` - Add filtering logic
- `apps/interns/views.py` - Add search functionality
- Templates - Add filter forms

---

### 8. Notification Digest Implementation

**Status:** Flags exist, scheduler not implemented  
**Current State:** User model has daily/weekly digest flags  
**What's Missing:**

- Celery/background task setup
- Daily digest email generation
- Weekly digest email generation
- Digest content aggregation
- Digest scheduling (cron job or Celery Beat)
- Unsubscribe functionality

**Implementation Steps:**

1. Install Celery: `pip install celery redis`
2. Configure Celery in `config/celery.py`
3. Create periodic tasks for digests
4. Create digest email templates
5. Aggregate notifications for digest

**Files to Create:**

- `config/celery.py` - Celery configuration
- `apps/notifications/tasks.py` - Celery tasks
- `apps/notifications/services.py` - Add digest generation methods
- `templates/emails/daily_digest.html`
- `templates/emails/weekly_digest.html`

---

### 9. Assessment Period Validation

**Status:** Field exists, not enforced  
**Current State:** Assessment has period fields  
**What's Missing:**

- Validate assessments only during assessment period
- Configure assessment periods globally
- Override periods per branch
- Warning when period is ending
- Lock assessments after period ends
- Assessment period calendar view

**Files to Modify:**

- `apps/evaluations/models.py` - Add validation logic
- `apps/evaluations/views.py` - Enforce period checks
- Create assessment period configuration interface

---

### 10. Acknowledgement Notes for Assessments

**Status:** Field exists, no form field  
**Current State:** Model has acknowledgement field  
**What's Missing:**

- Intern can add acknowledgement note
- Display acknowledgement in assessment detail
- Track when acknowledgement was added
- Require acknowledgement before closing assessment

**Files to Modify:**

- `apps/evaluations/forms.py` - Add acknowledgement field
- `templates/evaluations/intern_assessment_detail.html`
- `apps/evaluations/views.py` - Add acknowledgement logic

---

### 11. Branch Filtering in Attendance Views

**Status:** Partial implementation  
**What's Missing:**

- Filter attendance by branch in list views
- Branch-specific attendance reports
- Multi-branch comparison
- Branch performance dashboard

**Files to Modify:**

- `apps/attendance/views.py` - Add branch filtering
- `templates/attendance/list.html` - Add branch filter dropdown

---

### 12. Geolocation Detailed Storage

**Status:** Validated but not stored comprehensively  
**Current State:** Lat/lon stored, additional data available  
**What's Missing:**

- Store address from reverse geocoding
- Store accuracy consistently
- Store altitude (if needed)
- Store device information
- Map view of attendance locations
- Geofencing visualization

**Files to Modify:**

- `apps/attendance/models.py` - Add address fields
- `apps/attendance/views.py` - Add geocoding logic
- Install geocoding library: `pip install geopy`
- Create map view template with Leaflet or Google Maps

---

### 13. Intern Type Classification

**Status:** Field exists, values undefined  
**Current State:** InternProfile has intern_type field  
**What's Missing:**

- Define intern types (Full-time, Part-time, Remote, etc.)
- Add choices to model
- Filter/group by intern type
- Type-specific rules or workflows
- Reports by intern type

**Files to Modify:**

- `apps/interns/models.py` - Add TextChoices for intern_type
- Forms and templates to display/select type
- Migrations to update field

---

## 🟢 Nice to Have

### 14. Advanced Analytics & Reporting

**Status:** Basic PDF/CSV exports exist  
**What Could Be Added:**

- Interactive dashboards (Chart.js was added then removed)
- Trend analysis over time
- Predictive analytics
- Custom report builder
- Scheduled report generation
- Report templates

**Possible Libraries:**

- Chart.js for frontend charts
- Plotly for interactive visualizations
- Django Q or Celery for scheduled reports

---

### 15. Mobile Responsiveness Improvements

**Status:** Bootstrap responsive, but can be enhanced  
**What Could Be Improved:**

- Mobile-specific navigation
- Touch-optimized forms
- Offline capability (PWA)
- Mobile app considerations
- Better mobile map interactions

---

### 16. API for Mobile/External Integration

**Status:** Not implemented  
**What Could Be Built:**

- RESTful API with Django REST Framework
- JWT authentication
- API documentation (Swagger/OpenAPI)
- Rate limiting
- API versioning
- Mobile app backend

**Implementation:**

- Install DRF: `pip install djangorestframework`
- Create `apps/api/` with serializers and viewsets
- Add API documentation

---

### 17. Two-Factor Authentication (2FA)

**Status:** Not implemented  
**What's Needed:**

- TOTP-based 2FA
- SMS-based 2FA (optional)
- Backup codes
- 2FA setup flow
- Remember device option

**Libraries:**

- `django-otp` for TOTP
- `django-two-factor-auth` for complete solution

---

### 18. Audit Trail Enhancements

**Status:** Basic ActivityLog exists  
**What Could Be Added:**

- Track all CRUD operations automatically
- Store before/after values
- Audit log search and export
- Compliance reporting
- Data retention policies
- User activity timeline

---

### 19. Bulk Operations

**Status:** Not implemented  
**What Could Be Added:**

- Bulk approve/reject attendance
- Bulk intern assignment to branches
- Bulk notification sending
- Bulk assessment creation
- Import interns from CSV/Excel

**Files to Create:**

- Bulk action views and forms
- CSV import utilities
- Bulk operation templates

---

### 20. Holiday Calendar Integration

**Status:** Holiday model exists, limited integration  
**What Could Be Enhanced:**

- Display holidays in calendar view
- Automatic attendance handling on holidays
- Holiday impact on reports
- Multiple calendar support (different regions)
- Recurring holiday rules

**Files to Modify:**

- `apps/holidays/views.py` - Calendar view
- Integrate with attendance validation
- Add calendar widget to dashboard

---

### 21. Intern Performance Tracking

**Status:** Assessments exist, no comprehensive tracking  
**What Could Be Added:**

- Performance history timeline
- Skill development tracking
- Goal setting and tracking
- 360-degree feedback
- Performance improvement plans
- Competency matrix

---

### 22. Document Management System

**Status:** Basic file uploads only  
**What Could Be Built:**

- Centralized document library
- Version control for documents
- Document approval workflows
- Document categories and tags
- Search documents by content
- Document expiry tracking

---

### 23. Communication Features

**Status:** Only notifications exist  
**What Could Be Added:**

- Internal messaging between users
- Announcement system
- Discussion forums
- Video conferencing integration
- Chat functionality
- Email integration

---

### 24. Time Tracking Integration

**Status:** Check-in/out exists, basic tracking  
**What Could Be Enhanced:**

- Time tracking per project/task
- Timesheet approval workflow
- Overtime tracking
- Time-off balance tracking
- Integration with payroll systems
- Time tracking reports

---

### 25. Onboarding Workflow Enhancement

**Status:** Basic onboarding exists  
**What Could Be Added:**

- Multi-step onboarding wizard
- Welcome video/tutorial
- Onboarding checklist
- Mentor assignment
- Training module tracking
- Onboarding feedback survey

---

## 🔧 Technical Improvements

### 26. Testing Coverage

**Status:** Limited/no tests  
**What's Needed:**

- Unit tests for models
- Integration tests for views
- Form validation tests
- API tests (if API is built)
- End-to-end tests
- Test coverage reports

**Tools:**

- pytest-django
- coverage.py
- Factory Boy for test data

---

### 27. Performance Optimization

**What Could Be Done:**

- Database query optimization
- Add database indexes
- Implement caching (Redis)
- Lazy loading for images
- Database connection pooling
- CDN for static files

---

### 28. Security Enhancements

**What Could Be Added:**

- Rate limiting on login
- CAPTCHA on public forms
- Security headers (django-security)
- Content Security Policy
- Regular security audits
- Penetration testing
- GDPR compliance features

---

### 29. Deployment & DevOps

**What Could Be Improved:**

- CI/CD pipeline setup
- Automated testing in CI
- Staging environment
- Database backup automation
- Log aggregation (ELK stack)
- Monitoring (Sentry, New Relic)
- Container orchestration (Kubernetes)

---

### 30. Documentation

**What's Needed:**

- API documentation (if built)
- User manual/guide
- Admin guide
- Deployment guide
- Contributing guidelines
- Architecture documentation
- Database schema diagrams

---

## 📋 Quick Wins (Easy to Implement)

1. **Display Last Login Date** - Already tracked, just show it
2. **User Online Status Indicator** - Simple session-based check
3. **Dark Mode Toggle** - CSS-based theme switching
4. **Export Lists to Excel** - Similar to CSV, use openpyxl
5. **Breadcrumb Navigation** - Improve UX with breadcrumbs
6. **Loading Spinners** - Better UX for async operations
7. **Form Auto-save** - JavaScript-based localStorage save
8. **Keyboard Shortcuts** - Power user features
9. **Tooltips & Help Text** - Better user guidance
10. **Print-Friendly Views** - CSS print media queries

---

## 🎯 Implementation Priority Recommendation

### Phase 1 (Next 2-4 weeks):

1. Email Configuration ✅ Critical
2. Profile Picture Upload ✅ User-facing
3. Emergency Contact Form ✅ Data completion
4. Activity Log UI ✅ Admin needs

### Phase 2 (1-2 months):

5. Search & Filtering ✅ User experience
6. Notification Digests ✅ Reduce email clutter
7. Assessment Period Validation ✅ Business logic
8. Document Preview ✅ User experience

### Phase 3 (2-3 months):

9. Geolocation Enhancement ✅ Better data
10. Bulk Operations ✅ Admin efficiency
11. Advanced Reporting ✅ Insights
12. Mobile Improvements ✅ Accessibility

### Phase 4 (3+ months):

13. API Development ✅ External integration
14. Performance Optimization ✅ Scalability
15. Testing Coverage ✅ Stability
16. Advanced Features ✅ Nice to have

---

## 📝 Notes

- This list was compiled based on codebase analysis and identified unused features
- Priority levels are suggestions and may be adjusted based on business needs
- Some features may have partial implementations that need completion
- Always backup database before implementing major changes
- Test thoroughly in development before deploying to production
- Consider user feedback when prioritizing features

---

## 🔗 Related Files

- **Models:** Check all `models.py` files for unused fields
- **Forms:** Review `forms.py` files for incomplete forms
- **Views:** Check `views.py` for TODO comments
- **Templates:** Look for disabled/commented sections
- **Settings:** Review `config/settings.py` for configurations

---

## 💡 Getting Started

To work on any of these features:

1. Create a new branch: `git checkout -b feature/feature-name`
2. Implement the feature with tests
3. Update this TODO.md to mark feature as complete
4. Create a pull request with detailed description
5. Test in staging before production deployment

---

**Good luck with your implementation! 🚀**
