# Internship Management System – Architecture Kickoff

## 1. High-Level System Overview

- **Backend:** Django (latest LTS) with Django REST Framework (for future API needs) sitting on PostgreSQL. Optional PostGIS extension for geospatial attendance validation.
- **Deployment:** Docker Compose orchestrating `web`, `db`, `worker`, and `scheduler` services. Gunicorn + Nginx can be introduced later for production.
- **Frontend:** Django template engine adhering to Human Interface Guidelines. Leverage HTMX or Alpine.js for progressive enhancements where useful.
- **Task Processing:** Celery with Redis (optional for MVP) for queued notifications and PDF generation.
- **Media/Static:** Django storage backed initially by local volume; ready to swap in S3-compatible storage for production.

## 2. Domain-Driven App Layout

| App                        | Responsibility                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `accounts`                 | Custom `User` model, roles (intern, employee, supervisor, manager, admin), onboarding links, authentication flows. |
| `interns`                  | Intern demographic data, school links, branch assignment, uploaded documents, status.                              |
| `schools`                  | School entities and `AcademicSupervisor` reference data.                                                           |
| `supervisors`              | Internal employee directory, roles, permissions, branch bindings.                                                  |
| `branches`                 | Branch metadata, geo-coordinates, branch employee assignments, holidays.                                           |
| `evaluations`              | Weekly/periodic assessments, supervisor + self assessments, scoring rubrics.                                       |
| `attendance`               | Check-ins, geo-validation, approval workflow, history views.                                                       |
| `absenteeism`              | Time-off requests, approval chain, notifications.                                                                  |
| `holidays`                 | Branch-level holidays affecting attendance logic.                                                                  |
| `log`                      | Activity log aggregator spanning all critical actions.                                                             |
| `notifications` (optional) | Email + in-app notification delivery, templating, scheduling.                                                      |

## 3. Core Data Model Relationships

- `accounts.User` (Custom user) has OneToOne to specialized profiles (`interns.InternProfile`, `supervisors.EmployeeProfile`). Roles drive dashboard access.
- `interns.InternProfile` → FK to `schools.School`, optional FK to `schools.AcademicSupervisor`, FK to `branches.Branch`, ManyToMany to `supervisors.EmployeeProfile` for supervisors.
- `evaluations.PerformanceAssessment` links intern, assessor (supervisor or manager), week number/period, supervisor remarks, intern self assessment (one-to-one per period) captured via nested model or JSON field.
- `attendance.AttendanceRecord` includes intern, branch, check-in time, check-out (optional), location (geospatial point), approval flag, auto-validated distance column.
- `absenteeism.AbsenteeismRequest` ties intern, approver (supervisor/manager), status workflow, optional attachments, activity log hook.
- `log.ActivityLog` uses generic foreign key to reference any model, stores actor, action, metadata JSON.

## 4. Service Modules & Cross-Cutting Concerns

- **Geo Service:** Abstraction around geopy/PostGIS distance calculations with configurable thresholds per branch.
- **Notification Service:** Pluggable channels (email via Django EmailBackend, in-app via database) with Celery tasks.
- **PDF Service:** Wrapper around WeasyPrint/xhtml2pdf for reports and exports.
- **Audit Middleware:** Signal listeners hooking into create/update/delete events to populate `ActivityLog`.

## 5. Configuration & Settings Strategy

- `.env` driven settings (DJANGO_SETTINGS_MODULE, DB URL, email, Redis, S3).
- Split settings modules: `settings/base.py`, `settings/dev.py`, `settings/prod.py`.
- Feature flags for geolocation enforcement and notification channels.

## 6. Initial Milestones

1. **Milestone 0 – Scaffold**
   - Docker Compose (web, db, redis placeholder), Django project skeleton, shared settings, custom user model stub, basic README.
2. **Milestone 1 – Accounts & Onboarding**
   - User registration/onboarding, role-based dashboards (skeleton), secure invite links, login flow.
3. **Milestone 2 – Intern Lifecycle**
   - Intern profiles, school linkage, document uploads, branch assignment, supervisor assignments.
4. **Milestone 3 – Attendance & Geo Validation**
   - Attendance check-in/out, geolocation service, proximity configuration, holiday integration.
5. **Milestone 4 – Assessments & Absenteeism**
   - Performance assessments (supervisor + self), absenteeism requests, notifications.
6. **Milestone 5 – Reporting & Logs**
   - Activity logs UI, CSV/PDF exports, dashboard enhancements, analytics widgets.
7. **Milestone 6 – QA & Hardening**
   - Comprehensive tests, security hardening, production deployment scripts.

## 7. Testing Approach

- Pytest or Django test framework with factories (Factory Boy).
- Unit tests for models, services, and signals.
- Integration tests covering attendance geo-approval, assessment workflow, notifications.
- Linting via `ruff`/`black`, type checking via `mypy` (optional).

## 8. Open Questions / Assumptions

- Assume PostGIS is optional; fallback to `geopy` distance calculations if extension unavailable.
- Email provider unspecified; default to console backend in dev.
- Notification UI will start simple (badge + list) and iterate.
- No dedicated API consumers yet, but DRF inclusion keeps expansion possible.

---

This document should evolve as we deepen implementation details and discover new requirements.
