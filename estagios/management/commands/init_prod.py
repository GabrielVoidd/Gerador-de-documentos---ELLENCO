import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Initialize production data'

    def handle(self, *args, **options):
        User = get_user_model()

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='souza',
                email=os.environ.get('ADMIN_EMAIL', 'sollencomktdigital@gmail.com'),
                password=os.environ.get('ADMIN_PASSWORD', 'qazwsx')
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser criado com sucesso')
            )
        else:
            self.stdout.write(
                self.style.WARNING('O Superuser já existe')
            )
