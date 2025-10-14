# Internship Management System

A Django-based platform for hospitals to manage interns, supervisors, attendance, assessments, and reporting. The system is designed to support onboarding workflows, geolocation-based attendance validation, PDF report generation, and detailed activity logging.

## Features

- Secure onboarding with time-bound invitations and configurable roles.
- Comprehensive intern profiles with school affiliations, supervisors, and documentation.
- Branch management and proximity-based attendance approvals.
- Weekly/periodic performance assessments with supervisor and self-assessment feedback.
- Absenteeism request workflows and holiday scheduling.
- Activity logging for auditability and compliance.
- Docker Compose environment with PostgreSQL.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- (Optional) Python 3.11+ if running locally without Docker

### Environment Configuration

Duplicate the `.env.example` file to `.env` and adjust values as needed:

```bash
cp .env.example .env
```

### Run with Docker

```bash
docker-compose up -d
```

The application will be available at <http://localhost:8000>. Access the Django admin at `/admin/`.

**Default Admin Credentials:**

- Username: `admin`
- Password: `admin123`

**Note:** Change the default admin password in production by running:

```bash
docker-compose exec web python manage.py changepassword admin
```

### Run Locally (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Tests

Testing scaffolding will be added as business logic evolves. Planned coverage includes unit tests for attendance validation, onboarding workflows, and assessment logic.

## License

This project is private and intended for internal hospital use. Consult project stakeholders for licensing details.
