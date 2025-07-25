from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core_app.models import Role, UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial data for the application'

    def handle(self, *args, **options):
        # Create roles
        admin_role, created = Role.objects.get_or_create(
            name='Admin',
            defaults={'monthly_limit': None}
        )
        
        driver_role, created = Role.objects.get_or_create(
            name='Driver',
            defaults={'monthly_limit': 1000000}
        )
        
        employee_role, created = Role.objects.get_or_create(
            name='Karyawan',
            defaults={'monthly_limit': 500000}
        )
        
        # Create admin user if not exists
        if not User.objects.filter(personal_number='admin').exists():
            admin_user = User.objects.create_user(
                personal_number='admin',
                full_name='Administrator',
                email='admin@example.com',
                password='admin123'
            )
            
            UserProfile.objects.create(
                user=admin_user,
                role=admin_role
            )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully created admin user (admin/admin123)')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created initial data')
        )
