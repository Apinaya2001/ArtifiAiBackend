# from django.apps import AppConfig


# class AccountsConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'accounts'
# accounts/apps.py (optional signal wiring)
# from django.apps import AppCompatActivity as AppConfig
from django.apps import AppConfig 
class AccountsConfig(AppConfig):
    name = 'accounts'
    def ready(self):
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save
        from profiles.models import Profile
        def create_profile(sender, instance, created, **kwargs):
            if created: Profile.objects.get_or_create(user=instance)
        post_save.connect(create_profile, sender=User)
