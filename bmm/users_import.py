from django.core.management import setup_environ
import settings
setup_environ(settings)

import os
import sys
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from django.contrib.auth.models import User, Group

def create_users():
    import csv
    reader = csv.reader(open("../data/email_list.csv",'rb'))
    reader.next()
    group = Group.objects.get(name='Community Members')
    users = []
    for row in reader:
        email = row[0].strip().lower()
        first_name = row[1]
        first_name_cleaned = first_name.replace('-',' ').title().replace(' ', '')
        last_name = row[2]
        last_name_cleaned = last_name.replace('-',' ').title().replace(' ', '')
        username = first_name_cleaned + last_name_cleaned
        user = User.objects.create_user(username, email, 'resilience')
        user.first_name = first_name
        user.last_name = last_name
        user.is_staff = False
        user.is_superuser = False
        user.groups = [group]
        user.save()
        print user.username, user.groups
        


if __name__ == '__main__':
    create_users()

