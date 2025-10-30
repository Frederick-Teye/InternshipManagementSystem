# Database Inventory - Internship Management System

**Generated:** October 30, 2025  
**Database:** PostgreSQL  
**Django Version:** 4.2.11

---

## 📊 Executive Summary

### Total Database Tables

| Category                      | Count |
| ----------------------------- | ----- |
| **Custom Application Tables** | 16    |
| **Django Built-in Tables**    | ~10   |
| **Total Tables**              | ~26   |

### Tables by Application

| Application       | Tables | Purpose                                  |
| ----------------- | ------ | ---------------------------------------- |
| **accounts**      | 2      | User authentication and onboarding       |
| **interns**       | 2      | Intern profiles and types                |
| **schools**       | 2      | Educational institutions and supervisors |
| **supervisors**   | 1      | Employee/supervisor profiles             |
| **branches**      | 2      | Hospital branches and assignments        |
| **attendance**    | 1      | Attendance tracking with geolocation     |
| **evaluations**   | 1      | Performance assessments                  |
| **absenteeism**   | 1      | Absence request management               |
| **holidays**      | 1      | Branch-specific holidays                 |
| **notifications** | 2      | In-app and email notifications           |
| **reports**       | 0      | No models defined                        |
| **dashboards**    | 0      | No models (views only)                   |

---

## 🗂️ Detailed Table Documentation

### 1. Authentication & User Management (accounts)

#### 1.1 User (accounts_user)

**Extends:** Django's AbstractUser  
**Purpose:** Core user model with role-based access control

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `username` - Unique username (inherited)
- `email` - Unique email address
- `role` - User role (intern, employee, supervisor, manager, admin)
- `profile_picture` - User profile photo
- `is_onboarded` - Onboarding completion status
- `onboarding_token` - UUID for secure onboarding links
- `onboarding_token_expires_at` - Token expiration timestamp
- `first_name`, `last_name` - User name fields (inherited)
- `is_active`, `is_staff`, `is_superuser` - Permission flags (inherited)
- `date_joined`, `last_login` - Activity timestamps (inherited)

**Relationships:**

- OneToOne → InternProfile (interns)
- OneToOne → EmployeeProfile (supervisors)
- OneToMany → Notification (as recipient)
- OneToMany → Attendance (as recorded_by, approved_by)
- OneToMany → AbsenteeismRequest (as approver)
- OneToOne → NotificationPreference

**Business Rules:**

- Email must be unique
- Onboarding tokens expire after configurable TTL (default 24 hours)
- Role determines dashboard access and permissions

---

#### 1.2 OnboardingInvitation (accounts_onboardinginvitation)

**Purpose:** Tracks secure onboarding invitation links

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `user_id` (FK) - Related user account
- `token` - UUID4 unique token
- `expires_at` - Invitation expiration timestamp
- `created_at` - Creation timestamp
- `used` - Whether invitation has been redeemed

**Relationships:**

- OneToOne → User (cascade on delete)

**Business Rules:**

- Token must be unique
- Invitation is invalid after expiration or use
- One invitation per user

---

### 2. Intern Management (interns)

#### 2.1 InternType (interns_interntype)

**Purpose:** Categorizes intern types (e.g., clinical, administrative)

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `name` - Unique internal name
- `display_name` - Human-readable name

**Relationships:**

- OneToMany → InternProfile

**Business Rules:**

- Name must be unique
- Ordered alphabetically

---

#### 2.2 InternProfile (interns_internprofile)

**Purpose:** Extended profile information for intern users

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `user_id` (FK) - Related User account
- `school_id` (FK) - Educational institution
- `academic_supervisor_id` (FK) - Academic supervisor from school
- `branch_id` (FK) - Assigned hospital branch
- `internal_supervisor_id` (FK) - Internal supervisor (EmployeeProfile)
- `intern_type_id` (FK) - Type of internship
- `profile_picture` - Profile photo upload
- `application_letter` - Application document upload
- `start_date` - Internship start date
- `end_date` - Internship end date
- `emergency_contact_name` - Emergency contact
- `emergency_contact_phone` - Emergency phone
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- OneToOne → User (cascade on delete)
- ManyToOne → School (set null on delete)
- ManyToOne → AcademicSupervisor (set null on delete)
- ManyToOne → Branch (set null on delete)
- ManyToOne → EmployeeProfile (set null on delete)
- ManyToOne → InternType (set null on delete)
- OneToMany → Attendance
- OneToMany → PerformanceAssessment
- OneToMany → AbsenteeismRequest

**Business Rules:**

- Active status determined by start_date and end_date
- File uploads stored in media/interns/
- Ordered by user's last name, first name

---

### 3. Educational Institutions (schools)

#### 3.1 School (schools_school)

**Purpose:** Represents educational institutions sending interns

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `name` - Unique school name
- `type` - Institution type (e.g., university, college)
- `contact_email` - Primary contact email
- `contact_phone` - Primary contact phone
- `address_line1`, `address_line2` - Street address
- `city`, `state`, `country` - Location details
- `website` - School website URL
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- OneToMany → InternProfile
- OneToMany → AcademicSupervisor

**Business Rules:**

- School name must be unique
- Ordered alphabetically by name

---

#### 3.2 AcademicSupervisor (schools_academicsupervisor)

**Purpose:** Faculty members supervising interns from their institution

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `school_id` (FK) - Associated school
- `first_name`, `last_name` - Supervisor name
- `email` - Unique contact email
- `phone_number` - Contact phone
- `title` - Academic title (e.g., Professor, Dr.)
- `notes` - Additional information
- `is_active` - Active status flag
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- ManyToOne → School (cascade on delete)
- OneToMany → InternProfile

**Business Rules:**

- Email must be globally unique
- (school, email) combination must be unique
- Ordered by last name, first name

---

### 4. Employee/Supervisor Management (supervisors)

#### 4.1 EmployeeProfile (supervisors_employeeprofile)

**Purpose:** Extended profile for employee and supervisor users

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `user_id` (FK) - Related User account
- `job_title` - Employee position title
- `phone_number` - Contact phone
- `department` - Department/unit assignment
- `bio` - Employee bio/description
- `is_clinical_supervisor` - Clinical supervisor flag
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- OneToOne → User (cascade on delete)
- OneToMany → InternProfile (as internal_supervisor)
- OneToMany → PerformanceAssessment (as assessed_by)
- OneToMany → BranchEmployeeAssignment

**Business Rules:**

- One profile per user
- Role from User.role property

---

### 5. Branch Management (branches)

#### 5.1 Branch (branches_branch)

**Purpose:** Hospital branches where interns are assigned

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `name` - Unique branch name
- `code` - Unique branch code
- `address_line1`, `address_line2` - Street address
- `city`, `state`, `country` - Location details
- `latitude` - GPS latitude (12 digits, 9 decimal places)
- `longitude` - GPS longitude (12 digits, 9 decimal places)
- `proximity_threshold_meters` - Auto-approval distance (default: 150m)
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- OneToMany → InternProfile
- OneToMany → Attendance
- OneToMany → Holiday
- OneToMany → BranchEmployeeAssignment

**Business Rules:**

- Both name and code must be unique
- GPS coordinates used for geofencing
- Ordered alphabetically by name

---

#### 5.2 BranchEmployeeAssignment (branches_branchemployeeassignment)

**Purpose:** Links employees to branches with specific roles

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `branch_id` (FK) - Assigned branch
- `employee_id` (FK) - Assigned employee
- `role` - Assignment role (supervisor, manager, coordinator)
- `is_primary` - Primary assignment flag
- `assigned_at` - Assignment timestamp
- `active` - Active status flag

**Relationships:**

- ManyToOne → Branch (cascade on delete)
- ManyToOne → EmployeeProfile (cascade on delete)

**Business Rules:**

- (branch, employee, role) combination must be unique
- Supports multiple roles per employee

---

### 6. Attendance Tracking (attendance)

#### 6.1 Attendance (attendance_attendance)

**Purpose:** GPS-based attendance check-in/out records

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `intern_id` (FK) - Intern checking in
- `branch_id` (FK) - Branch location
- `check_in_time` - Check-in timestamp
- `check_out_time` - Check-out timestamp (nullable)
- `latitude` - Check-in GPS latitude (10 digits, 7 decimal places)
- `longitude` - Check-in GPS longitude (10 digits, 7 decimal places)
- `location_accuracy_m` - GPS accuracy in meters
- `approval_status` - Status (pending, approved, rejected)
- `auto_approved` - Auto-approval flag
- `notes` - Additional notes/reasons
- `recorded_by_id` (FK) - User who recorded entry
- `approved_by_id` (FK) - User who approved/rejected
- `approved_at` - Approval timestamp
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- ManyToOne → InternProfile (cascade on delete)
- ManyToOne → Branch (cascade on delete)
- ManyToOne → User (as recorded_by, approved_by, set null on delete)

**Business Rules:**

- Auto-approved if within branch proximity threshold
- Uses Haversine formula for distance calculation
- Ordered by check-in time (descending)

---

### 7. Performance Evaluation (evaluations)

#### 7.1 PerformanceAssessment (evaluations_performanceassessment)

**Purpose:** Weekly intern performance assessments

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `intern_id` (FK) - Assessed intern
- `assessed_by_id` (FK) - Supervisor conducting assessment
- `assessment_date` - Assessment date
- `period_start`, `period_end` - Assessment period dates
- `week_number` - Week number in internship
- `status` - Status (draft, submitted, reviewed)
- `supervisor_score` - Supervisor score (0-100)
- `supervisor_note` - Supervisor feedback
- `intern_score` - Intern self-assessment score (0-100)
- `intern_note` - Intern self-reflection
- `acknowledgement_note` - Completion remarks
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- ManyToOne → InternProfile (cascade on delete)
- ManyToOne → EmployeeProfile (set null on delete)

**Business Rules:**

- (intern, week_number) combination must be unique
- Scores range from 0-100
- Workflow: Draft → Submitted → Reviewed
- Ordered by assessment date (descending)

---

### 8. Absence Management (absenteeism)

#### 8.1 AbsenteeismRequest (absenteeism_absenteeismrequest)

**Purpose:** Intern absence/leave requests

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `intern_id` (FK) - Requesting intern
- `approver_id` (FK) - Approving user
- `status` - Status (pending, approved, rejected, cancelled)
- `reason` - Absence reason (text)
- `start_date` - Absence start date
- `end_date` - Absence end date
- `supporting_document` - Document upload
- `submitted_at` - Submission timestamp
- `decision_at` - Decision timestamp
- `decision_note` - Approval/rejection notes

**Relationships:**

- ManyToOne → InternProfile (cascade on delete)
- ManyToOne → User (as approver, set null on delete)

**Business Rules:**

- Documents stored in media/absenteeism/
- Can be cancelled by intern before approval
- Ordered by submission time (descending)

---

### 9. Holiday Management (holidays)

#### 9.1 Holiday (holidays_holiday)

**Purpose:** Branch-specific or system-wide holidays

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `branch_id` (FK) - Related branch (nullable for system-wide)
- `name` - Holiday name
- `date` - Holiday date
- `is_full_day` - Full day holiday flag
- `description` - Holiday description
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- ManyToOne → Branch (cascade on delete, nullable)

**Business Rules:**

- Null branch means applies to all branches
- (branch, date, name) combination must be unique
- Ordered by date, name

---

### 10. Notification System (notifications)

#### 10.1 Notification (notifications_notification)

**Purpose:** In-app notification messages for users

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `recipient_id` (FK) - User receiving notification
- `title` - Notification title (max 255 chars)
- `message` - Detailed message text
- `notification_type` - Visual type (info, success, warning, error)
- `category` - Category (attendance, assessment, absenteeism, onboarding, system, general)
- `is_read` - Read status flag
- `read_at` - Read timestamp
- `action_url` - Optional URL for click action (max 500 chars)
- `content_type_id` (FK) - Generic relation content type
- `object_id` - Generic relation object ID
- `related_object` - GenericForeignKey to any model
- `email_sent` - Email sent flag
- `email_sent_at` - Email sent timestamp
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- ManyToOne → User (cascade on delete)
- GenericForeignKey → Any model (via ContentType)

**Database Indexes:**

- (recipient, created_at) - For efficient user notification queries
- (recipient, is_read) - For unread count queries
- (category) - For category filtering

**Business Rules:**

- Ordered by creation time (descending)
- Supports generic relations to attendance, assessments, etc.
- Email notification optional

---

#### 10.2 NotificationPreference (notifications_notificationpreference)

**Purpose:** User preferences for notification delivery

**Key Fields:**

- `id` (PK) - Auto-incrementing primary key
- `user_id` (FK) - Related user
- `email_on_attendance_approval` - Email for attendance status (default: true)
- `email_on_assessment_created` - Email for new assessments (default: true)
- `email_on_assessment_reviewed` - Email for assessment reviews (default: true)
- `email_on_absence_status` - Email for absence status (default: true)
- `email_on_onboarding` - Email for onboarding events (default: true)
- `in_app_notifications` - Show in-app notifications (default: true)
- `daily_digest` - Daily digest option (default: false)
- `weekly_digest` - Weekly digest option (default: false)
- `created_at`, `updated_at` - Audit timestamps

**Relationships:**

- OneToOne → User (cascade on delete)

**Business Rules:**

- One preference record per user
- Auto-created on user registration
- Controls both in-app and email notifications

---

## 🔗 Relationship Summary

### Primary Relationships

| From Table               | Relationship      | To Table               | Type              |
| ------------------------ | ----------------- | ---------------------- | ----------------- |
| User                     | OneToOne          | InternProfile          | 1:1               |
| User                     | OneToOne          | EmployeeProfile        | 1:1               |
| User                     | OneToOne          | NotificationPreference | 1:1               |
| User                     | OneToOne          | OnboardingInvitation   | 1:1               |
| InternProfile            | ManyToOne         | School                 | N:1               |
| InternProfile            | ManyToOne         | Branch                 | N:1               |
| InternProfile            | ManyToOne         | EmployeeProfile        | N:1               |
| InternProfile            | ManyToOne         | InternType             | N:1               |
| AcademicSupervisor       | ManyToOne         | School                 | N:1               |
| Attendance               | ManyToOne         | InternProfile          | N:1               |
| Attendance               | ManyToOne         | Branch                 | N:1               |
| PerformanceAssessment    | ManyToOne         | InternProfile          | N:1               |
| PerformanceAssessment    | ManyToOne         | EmployeeProfile        | N:1               |
| AbsenteeismRequest       | ManyToOne         | InternProfile          | N:1               |
| Holiday                  | ManyToOne         | Branch                 | N:1 (nullable)    |
| BranchEmployeeAssignment | ManyToOne         | Branch                 | N:1               |
| BranchEmployeeAssignment | ManyToOne         | EmployeeProfile        | N:1               |
| Notification             | ManyToOne         | User                   | N:1               |
| Notification             | GenericForeignKey | Any Model              | N:1 (polymorphic) |

---

## 📈 Database Statistics

### Table Counts

- **Custom Models:** 16 tables
- **Django Auth:** ~3 tables (User, Group, Permission)
- **Django Sessions:** 1 table
- **Django ContentTypes:** 1 table
- **Django Sites:** 1 table
- **Django Admin:** 1 table
- **Total Estimated:** ~26 tables

### Field Type Distribution

- **Primary Keys (id):** 16 fields
- **Foreign Keys:** ~28 fields
- **OneToOne Fields:** 5 fields
- **Boolean Fields:** ~15 fields
- **DateTime Fields:** ~30 fields
- **CharField Fields:** ~50 fields
- **TextField Fields:** ~10 fields
- **Decimal Fields:** 6 fields (GPS coordinates)
- **Integer Fields:** ~8 fields
- **File/Image Fields:** 4 fields
- **Email Fields:** ~6 fields

### Relationships

- **OneToOne Relationships:** 5
- **ForeignKey Relationships:** ~28
- **Generic Relations:** 1 (Notification)
- **Unique Constraints:** ~12
- **Unique Together Constraints:** 5
- **Database Indexes:** 3 custom indexes (notifications)

---

## 🗄️ Storage Estimates

### Media Files

- **Profile Pictures:** `media/profiles/`, `media/interns/profile_photos/`
- **Application Documents:** `media/interns/application_letters/`
- **Absenteeism Documents:** `media/absenteeism/supporting_documents/`

### Expected Data Volume (1 Year, 100 Interns)

| Table                 | Estimated Rows | Notes                            |
| --------------------- | -------------- | -------------------------------- |
| User                  | ~120           | Interns + supervisors + staff    |
| InternProfile         | ~100           | One per intern                   |
| EmployeeProfile       | ~20            | Supervisors and managers         |
| School                | ~10            | Educational institutions         |
| Branch                | ~5             | Hospital branches                |
| Attendance            | ~22,000        | 100 interns × 220 working days   |
| PerformanceAssessment | ~5,200         | 100 interns × 52 weeks           |
| AbsenteeismRequest    | ~500           | ~5 requests per intern per year  |
| Notification          | ~50,000        | Multiple notifications per event |
| Holiday               | ~50            | ~10 holidays × 5 branches        |
| **Total Records**     | **~77,900**    | Approximate annual volume        |

### Database Size Estimate

- **Data Only:** ~50-100 MB (first year)
- **With Indexes:** ~75-150 MB
- **With Media Files:** Variable (depends on uploads)

---

## 🔐 Security Considerations

### Sensitive Data

- **User Credentials:** Hashed passwords in User table
- **Personal Information:** Names, emails, phone numbers
- **Emergency Contacts:** Stored in InternProfile
- **GPS Coordinates:** Location data in Attendance records
- **Assessment Data:** Performance scores and feedback
- **Medical Documents:** Absenteeism supporting documents

### Access Control

- Role-based access via User.role field
- Permissions enforced at Django view level
- Foreign key relationships respect cascade rules

---

## 🔄 Data Lifecycle

### User Onboarding Flow

1. **User** created with role
2. **OnboardingInvitation** generated with token
3. Token sent via email
4. User completes onboarding (is_onboarded = True)
5. **InternProfile** or **EmployeeProfile** created
6. **NotificationPreference** auto-created

### Intern Lifecycle Flow

1. **InternProfile** created with assignments
2. Daily **Attendance** records created
3. Weekly **PerformanceAssessment** records
4. Occasional **AbsenteeismRequest** records
5. **Notification** records for all events
6. Profile marked inactive after end_date

### Data Retention

- **Active Records:** All data retained
- **Completed Internships:** Historical data preserved
- **Cascade Deletes:** Configured per relationship
- **Soft Deletes:** Not currently implemented

---

## 📊 Query Patterns

### Most Frequent Queries

1. User authentication lookups (User table)
2. Dashboard statistics (aggregations across tables)
3. Pending approval lists (Attendance, AbsenteeismRequest)
4. Notification retrieval (Notification by recipient)
5. Intern profile lookups (InternProfile with relations)

### Complex Queries

- GPS distance calculations (Haversine formula)
- Performance trend analysis (PerformanceAssessment aggregations)
- Attendance reports with branch data
- Supervisor workload calculations

---

## 🏗️ Migration Status

**Current State:** All migrations applied  
**Migration Files:** Located in each app's `migrations/` directory  
**Database Schema:** PostgreSQL with appropriate field types

### Notable Migrations

- Initial auth system setup
- InternProfile type field addition
- Attendance geolocation fields
- Notification system with generic relations
- GPS coordinate precision updates

---

## 📝 Notes

### Design Patterns

- **Profile Pattern:** Extends User with OneToOne relationships
- **Audit Pattern:** created_at/updated_at timestamps on most models
- **Status Pattern:** Explicit status choices for workflows
- **Generic Relations:** Notification supports any related object

### Future Considerations

- Consider partitioning Attendance table by date
- Add database-level constraints for business rules
- Implement soft deletes for audit trail
- Add full-text search indexes for reports
- Consider read replicas for heavy reporting

---

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Maintained By:** Development Team
