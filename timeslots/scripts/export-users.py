from django.contrib.auth.models import User
import csv


def run():
    with open('/tmp/timeslots_user.csv', mode='w') as out_file:
        fieldnames = [
            'Firma',
            'UserID',
            'Rolle',
            # 'Aktiv',
            'Vorname',
            'Nachname',
        ]
        writer = csv.DictWriter(out_file, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_ALL, fieldnames=fieldnames)
        writer.writeheader()
        for user in User.objects.filter(is_active=True).order_by('username'):
            print(user.username)
            writer.writerow({
                'Firma': user.userprofile.company.encode('utf-8'),
                'UserID': user.username.encode('utf-8'),
                'Rolle': user.groups.first().name.encode('utf-8'),
                # 'Aktiv': user.is_active,
                'Vorname': user.first_name.encode('utf-8'),
                'Nachname': user.last_name.encode('utf-8'),
            })
