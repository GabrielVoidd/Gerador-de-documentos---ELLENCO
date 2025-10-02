from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    admin_username = os.environ.get('ADMIN_USERNAME', 'souza')
    admin_email = os.environ.get('ADMIN_EMAIL', 'sollencomktdigital@gmail.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if admin_password and not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(admin_username, admin_email, admin_password)
        print(f'Superuser "{admin_username}" criado')


class Migration(migrations.Migration):
    dependencies = [
        ('estagios', '0014_alter_candidato_idade_responsavel_legal_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
