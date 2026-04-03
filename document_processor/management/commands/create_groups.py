from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from document_processor.models import LoanAgreement

class Command(BaseCommand):
    help = 'Create default groups: Director, Moderator, Operator'

    def handle(self, *args, **options):
        groups = ['Director', 'Moderator', 'Operator']
        
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created group "{group_name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Group "{group_name}" already exists'))

        # Assign permissions (Subjective, adjust as needed)
        # Operator: Can add LoanAgreement
        # Moderator: Can change LoanAgreement
        # Director: Can view/change LoanAgreement
        
        try:
            content_type = ContentType.objects.get_for_model(LoanAgreement)
            permission_add = Permission.objects.get(codename='add_loanagreement', content_type=content_type)
            permission_change = Permission.objects.get(codename='change_loanagreement', content_type=content_type)
            permission_view = Permission.objects.get(codename='view_loanagreement', content_type=content_type)
            
            operator_group = Group.objects.get(name='Operator')
            operator_group.permissions.add(permission_add, permission_view)
            
            moderator_group = Group.objects.get(name='Moderator')
            moderator_group.permissions.add(permission_change, permission_view)
            
            director_group = Group.objects.get(name='Director')
            director_group.permissions.add(permission_change, permission_view)
            
            self.stdout.write(self.style.SUCCESS('Successfully assigned permissions'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error assigning permissions: {e}'))
