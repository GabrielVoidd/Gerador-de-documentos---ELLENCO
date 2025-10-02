from django.db import migrations
import os

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    admin_username = os.environ.get('ADMIN_USERNAME', 'admin_souza')
    admin_email = os.environ.get('ADMIN_EMAIL', 'sollencomktdigital@gmail.com')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if User.objects.filter(username=admin_username).exists():
        print(f'Superuser "{admin_username}" já existe')
        return

    if admin_password:
        User.objects.create_superuser(admin_username, admin_email, admin_password)
        print(f'Superuser "{admin_username}" criado')
    else:
        print('Senha do admin não definida - superuser não criado')


class Migration(migrations.Migration):
    dependencies = [
        ('estagios', '0014_alter_candidato_idade_responsavel_legal_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
