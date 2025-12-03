from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from tasks.models import Task, CustomUser


class Command(BaseCommand):
    help = 'Create role groups (Admin, Teacher, Student) and assign base permissions.'

    def handle(self, *args, **options):
        self.stdout.write('Creating role groups and assigning permissions...')

        # Task permissions
        task_ct = ContentType.objects.get_for_model(Task)
        task_perm_codenames = ['add_task', 'change_task', 'delete_task', 'view_task']
        task_perms = list(Permission.objects.filter(content_type=task_ct, codename__in=task_perm_codenames))

        # CustomUser permissions
        user_ct = ContentType.objects.get_for_model(CustomUser)
        user_perm_codenames = ['add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                               'manage_users', 'assign_roles', 'view_all_tasks']
        user_perms = list(Permission.objects.filter(content_type=user_ct, codename__in=user_perm_codenames))

        admin_perms = task_perms + user_perms
        teacher_perms = task_perms + [p for p in user_perms if p.codename == 'view_all_tasks']
        student_perms = [p for p in task_perms if p.codename == 'view_task']

        admin_group, _ = Group.objects.get_or_create(name='Admin')
        admin_group.permissions.set(admin_perms)

        teacher_group, _ = Group.objects.get_or_create(name='Teacher')
        teacher_group.permissions.set(teacher_perms)

        student_group, _ = Group.objects.get_or_create(name='Student')
        student_group.permissions.set(student_perms)

        self.stdout.write(self.style.SUCCESS('Groups and permissions created/updated.'))
