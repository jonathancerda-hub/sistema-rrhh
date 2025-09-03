import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo_rrhh.settings_hibrido')
django.setup()

from django.contrib.auth.models import User

print(f"Total usuarios: {User.objects.count()}")
for user in User.objects.all():
    print(f"- {user.username} ({user.first_name} {user.last_name})")
