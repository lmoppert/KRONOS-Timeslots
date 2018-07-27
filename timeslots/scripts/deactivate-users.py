from django.contrib.auth.models import User


def run():
    for user in User.objects.exclude(pk=1):
        user.is_active = False
        user.save()
