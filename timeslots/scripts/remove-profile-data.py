from timeslots import models

profiles = models.UserProfile.objects.all()
for profile in profiles:
    profile.street = ""
    profile.country = ""
    profile.phone = ""
    profile.ZIP = ""
    profile.town = ""
    profile.save()
