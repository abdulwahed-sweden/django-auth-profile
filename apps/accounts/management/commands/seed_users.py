from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


SEED_USERS = [
    {
        'username': 'erik.lindberg',
        'email': 'erik@example.se',
        'first_name': 'Erik',
        'last_name': 'Lindberg',
        'password': 'SwedishTest123!',
        'profile': {
            'location': 'Stockholm',
            'bio': 'Backend developer at Spotify',
            'phone': '+46 70 123 4501',
        },
    },
    {
        'username': 'anna.johansson',
        'email': 'anna@example.se',
        'first_name': 'Anna',
        'last_name': 'Johansson',
        'password': 'SwedishTest123!',
        'profile': {
            'location': 'Gothenburg',
            'bio': 'UX Designer at Klarna',
            'phone': '+46 70 123 4502',
        },
    },
    {
        'username': 'oscar.nilsson',
        'email': 'oscar@example.se',
        'first_name': 'Oscar',
        'last_name': 'Nilsson',
        'password': 'SwedishTest123!',
        'profile': {
            'location': 'Malmö',
            'bio': 'DevOps engineer at Ericsson',
            'phone': '+46 70 123 4503',
        },
    },
    {
        'username': 'sara.eriksson',
        'email': 'sara@example.se',
        'first_name': 'Sara',
        'last_name': 'Eriksson',
        'password': 'SwedishTest123!',
        'profile': {
            'location': 'Uppsala',
            'bio': 'Data scientist at IKEA Digital',
            'phone': '+46 70 123 4504',
        },
    },
    {
        'username': 'karl.svensson',
        'email': 'karl@example.se',
        'first_name': 'Karl',
        'last_name': 'Svensson',
        'password': 'SwedishTest123!',
        'profile': {
            'location': 'Linköping',
            'bio': 'Security researcher at SAAB',
            'phone': '+46 70 123 4505',
        },
    },
]


class Command(BaseCommand):
    help = 'Seed the database with sample Swedish users and an admin superuser'

    def handle(self, *args, **options):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@django.local',
                password='Admin123!',
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser created: {admin_user.username}'))
        else:
            self.stdout.write(self.style.WARNING('Superuser "admin" already exists, skipping.'))

        # Create seed users
        for data in SEED_USERS:
            username = data['username']
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'User "{username}" already exists, skipping.'))
                continue

            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )

            # Update profile (auto-created by signal)
            profile = user.profile
            profile.location = data['profile']['location']
            profile.bio = data['profile']['bio']
            profile.phone = data['profile']['phone']
            profile.save()

            self.stdout.write(self.style.SUCCESS(f'User created: {username} ({data["profile"]["location"]})'))

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
