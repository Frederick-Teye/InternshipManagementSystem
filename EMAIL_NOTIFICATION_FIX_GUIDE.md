# Email Notification Fix Guide

## Problem Identified

The internal app notifications work correctly, but email notifications are not being sent to users. This is due to email backend configuration issues.

## Root Cause Analysis

1. **Email Backend**: System is configured to use `console.EmailBackend` which prints emails to console instead of sending them
2. **Missing SMTP Credentials**: No email server credentials configured for actual email delivery
3. **Template Path Issue**: Fixed - notification email template was in wrong location

## Solutions

### Option 1: Development Testing (Console Output)

For development/testing, you can see email output in the console logs:

**Current Configuration (docker-compose.yml):**

```yaml
DJANGO_EMAIL_BACKEND: "django.core.mail.backends.console.EmailBackend"
```

**How to verify:**

1. Trigger a notification (approve attendance, submit assessment, etc.)
2. Check Docker container logs for email output:
   ```bash
   docker-compose logs web
   ```
3. You should see email content printed in the console

### Option 2: Real Email Sending (Production)

To send actual emails, configure SMTP settings:

**1. Update docker-compose.yml:**

```yaml
environment:
  # Email Configuration - SMTP backend for production
  DJANGO_EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend"
  DJANGO_EMAIL_HOST: "smtp.gmail.com"
  DJANGO_EMAIL_PORT: "587"
  DJANGO_EMAIL_USE_TLS: "true"
  DJANGO_EMAIL_HOST_USER: "your-email@gmail.com"
  DJANGO_EMAIL_HOST_PASSWORD: "your-app-password"
  DJANGO_DEFAULT_FROM_EMAIL: "noreply@internship.local"
```

**2. For Gmail Setup:**

- Use App Passwords (not regular password)
- Go to Google Account Settings > Security > App passwords
- Generate password for "Mail" application
- Use this password in `DJANGO_EMAIL_HOST_PASSWORD`

**3. For Other Email Providers:**

- **Outlook/Hotmail**: `smtp.live.com`, port 587, TLS
- **Yahoo**: `smtp.mail.yahoo.com`, port 587, TLS
- **Custom SMTP**: Use your organization's SMTP settings

## Testing Email Functionality

Use the provided test script:

```bash
docker-compose exec web python scripts/test_email.py
```

This script will:

- Show current email configuration
- Test basic email sending
- Test template-based emails
- Test notification emails
- Provide troubleshooting guidance

## Notification Triggers

Emails are sent for these events (when user has email notifications enabled):

### For Interns:

- ✅ Attendance approved/rejected
- ✅ Assessment created (new week)
- ✅ Assessment reviewed by supervisor
- ✅ Absence request approved/rejected

### For Supervisors:

- ✅ New absence request submitted
- ✅ Assessment ready for review

## User Email Preferences

Users can control email notifications in their profile:

**Settings Available:**

- Email on attendance approval/rejection
- Email on assessment created
- Email on assessment reviewed
- Email on absence status change
- Email on onboarding events
- Daily/weekly digest options

**Default Behavior:**

- All email notifications enabled by default
- Users can disable specific categories
- In-app notifications always work regardless of email settings

## Troubleshooting

### Issue: No emails in console (console backend)

**Solution:**

- Check if notifications are being created in database
- Verify user has email notifications enabled in preferences
- Check NotificationService is being called with `send_email=True`

### Issue: SMTP errors (production)

**Solutions:**

- Verify SMTP credentials are correct
- Check network connectivity to SMTP server
- Ensure app passwords are used (for Gmail)
- Check firewall settings

### Issue: Emails marked as spam

**Solutions:**

- Configure proper SPF/DKIM records
- Use reputable email service
- Include unsubscribe links
- Use professional from address

## Email Templates

Email templates are located in:

```
templates/
├── emails/
│   ├── base.html              # Base email template
│   ├── welcome.html           # Welcome email
│   └── onboarding_invitation.html
└── notifications/
    └── email/
        └── notification_email.html  # Notification emails
```

## Code Changes Made

1. **Fixed template path** in `apps/accounts/services.py`:

   ```python
   # Changed from:
   template_name="notification_email"
   # To:
   template_name="notifications/email/notification_email"
   ```

2. **Updated docker-compose.yml** with proper SMTP configuration

3. **Created test script** for email verification

## Next Steps

1. **Choose your email solution** (console for dev, SMTP for production)
2. **Update docker-compose.yml** with your email credentials
3. **Test email functionality** using the test script
4. **Verify user preferences** are configured correctly
5. **Monitor email delivery** in production

## Security Notes

- Never commit email passwords to git
- Use environment variables for sensitive configuration
- Consider using dedicated email service (SendGrid, Mailgun, etc.) for production
- Implement rate limiting for email sending
- Monitor for spam complaints

## Production Recommendations

For production deployment:

- Use dedicated email service (SendGrid, AWS SES, etc.)
- Implement email queuing for better performance
- Set up monitoring for email delivery rates
- Configure proper DNS records (SPF, DKIM, DMARC)
- Implement bounce and complaint handling
