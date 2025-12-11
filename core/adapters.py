from django.core.exceptions import ValidationError
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

ALLOWED_EMAIL_DOMAINS = ['bc.edu']  # Add the allowed domain here

class CustomAccountAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        email = super().clean_email(email)
        domain = email.split('@')[1]
        if domain not in ALLOWED_EMAIL_DOMAINS:
            raise ValidationError(
                f'You must sign up with a bc.edu email address. You entered {domain}.'
            )
        return email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get('email')
        if email:
            domain = email.split('@')[1]
            if domain not in ALLOWED_EMAIL_DOMAINS:
                raise ValidationError(
                    f'You must sign in with a bc.edu email address. You entered {domain}.'
                )
        return super().pre_social_login(request, sociallogin)