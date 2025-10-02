from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    admin_username = os.environ.get('ADMIN_USERNAME', 'souza')
    admin_email = os.environ.get('ADMIN_EMAIL', 'sollencomktdigital')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if admin_password and not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(admin_username, admin_email, admin_password)
        print(f'Superuser "{admin_username}" criado')


class Migrations(migrations.Migration):
    dependencies = [
        ('estagios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
