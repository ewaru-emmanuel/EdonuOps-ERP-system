# Email Verification Not Sending - Diagnosis

## Issue
User reports not receiving verification email after registration.

## Current Status
✅ Email service is already integrated in registration (line 457-478 in auth_enhanced.py)

## Potential Issues to Check

### 1. Email Service Configuration
Check if `.env` file has:
- `SES_SMTP_USER` - AWS SES SMTP username
- `SES_SMTP_PASS` - AWS SES SMTP password  
- `SES_FROM_EMAIL` - Sender email address (must be verified in SES)
- `FRONTEND_URL` - Frontend URL for verification links

### 2. Check Email Service Errors
Look for these log messages:
- `✅ Verification email sent to {email}` - Email sent successfully
- `⚠️  Failed to send verification email` - Email sending failed
- `❌ Error sending verification email` - Error occurred

### 3. AWS SES Configuration
- Sender email must be verified in AWS SES
- SMTP credentials must be correct
- Region should be `eu-north-1` (as configured)

### 4. Email Service Initialization
The email_service might fail to initialize if credentials are missing. Check:
- Is `EmailService()` initialization successful?
- Are there any import errors?

## Next Steps
1. Check server logs for email sending errors
2. Verify `.env` file has correct SES credentials
3. Test email service directly
4. Check AWS SES console for bounces/rejections


