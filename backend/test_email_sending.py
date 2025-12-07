#!/usr/bin/env python3
"""
Test email sending functionality
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv('.env')

print("🔍 Testing email service configuration...\n")

# Check environment variables
print("1. Checking environment variables:")
ses_user = os.getenv("SES_SMTP_USER")
ses_pass = os.getenv("SES_SMTP_PASS")
from_email = os.getenv("SES_FROM_EMAIL", "info@edonuerp.com")

if ses_user:
    print(f"   ✅ SES_SMTP_USER: {ses_user[:10]}...")
else:
    print(f"   ❌ SES_SMTP_USER: NOT SET")

if ses_pass:
    print(f"   ✅ SES_SMTP_PASS: {'*' * len(ses_pass)}")
else:
    print(f"   ❌ SES_SMTP_PASS: NOT SET")

print(f"   📧 FROM_EMAIL: {from_email}")

# Try to initialize email service
print("\n2. Testing email service initialization:")
try:
    from services.email_service import get_email_service
    email_service = get_email_service()
    if email_service:
        print("   ✅ Email service initialized successfully")
        
        # Try to send a test email
        print("\n3. Testing email send:")
        print("   (Skipping actual send - would send to real email)")
        print("   To test sending, uncomment the send_email call below")
        
        # Uncomment to actually send test email:
        # test_email = "your-email@example.com"
        # result = email_service.send_verification_email(test_email, 999, None)
        # if result:
        #     print(f"   ✅ Test email sent to {test_email}")
        # else:
        #     print(f"   ❌ Failed to send test email")
        
    else:
        print("   ❌ Email service initialization failed")
except Exception as e:
    print(f"   ❌ Error initializing email service: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Email service test complete!")


