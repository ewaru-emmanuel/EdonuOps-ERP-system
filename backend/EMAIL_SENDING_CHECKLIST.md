# Email Verification Email Not Received - Checklist

## ✅ Code Status
- Email service is properly integrated (lines 457-478 in auth_enhanced.py)
- Email service is configured correctly (SMTP credentials found)
- Error handling is in place

## 🔍 Things to Check

### 1. Check Server Logs
When you register, look for these messages in the server console:
- `📧 ✅ Verification email sent to {email}` - Email sent successfully
- `⚠️  Warning: Failed to send verification email to {email}` - Email sending failed
- `❌ Error sending verification email: {error}` - Error occurred

### 2. Check Email Service Errors
The email service logs errors. Check for:
- SMTP connection errors
- Authentication failures
- Email format issues

### 3. AWS SES Configuration
- **Sender Email**: Must be verified in AWS SES console
  - Check: AWS Console → SES → Verified Identities
  - The `SES_FROM_EMAIL` (info@edonuerp.com) must be verified
  
- **SES Sandbox Mode**: If in sandbox, can only send to verified emails
  - Solution: Request production access OR verify the recipient email

- **SMTP Credentials**: Must be valid
  - Check: AWS Console → SES → SMTP Settings
  - Verify the credentials match your .env file

### 4. Check Email Inbox
- Check spam/junk folder
- Wait a few minutes (SES can have delays)
- Check if email provider is blocking AWS SES

### 5. Test Email Sending Directly
Run the test script:
```bash
cd backend
python test_email_sending.py
```

## 🔧 Next Steps
1. Check server logs during registration for email errors
2. Verify sender email in AWS SES console
3. Check if recipient email needs to be verified (sandbox mode)
4. Check spam folder
5. Review AWS SES sending statistics

## 📝 Common Issues
- **Sandbox Mode**: Can only send to verified emails
- **Unverified Sender**: Sender email must be verified in SES
- **Spam Folder**: Emails might be in spam
- **SMTP Auth Failure**: Wrong credentials
- **Rate Limits**: Too many emails sent


