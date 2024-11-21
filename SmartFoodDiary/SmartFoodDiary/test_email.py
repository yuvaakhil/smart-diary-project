from django.core.mail import send_mail
from django.conf import settings

def test_email():
    try:
        send_mail(
            'Test Email',  # Subject
            'This is a test email from Django.',  # Body
            settings.EMAIL_HOST_USER,  # From email
            ['yuvaakhil815@gmail.com'],  # Replace with your recipient email
            fail_silently=False,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Ensure Django settings are loaded
if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SmartFoodDiary.settings')  # Replace with your settings module
    django.setup()
    test_email()
