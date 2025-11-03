from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    Task = apps.get_model('tasks', 'Task')
    CustomUser = apps.get_model('tasks', 'CustomUser')

    # Task permissions
    task_ct = ContentType.objects.get_for_model(Task)
    task_perm_codenames = ['add_task', 'change_task', 'delete_task', 'view_task']
    task_perms = list(Permission.objects.filter(content_type=task_ct, codename__in=task_perm_codenames))

    # CustomUser permissions and custom perms
    user_ct = ContentType.objects.get_for_model(CustomUser)
    user_perm_codenames = ['add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                           'manage_users', 'assign_roles', 'view_all_tasks']
    user_perms = list(Permission.objects.filter(content_type=user_ct, codename__in=user_perm_codenames))

    # Admin: all task perms + user perms
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    admin_group.permissions.set(task_perms + user_perms)

    # Teacher: task perms but remove delete_task (do not allow global delete)
    teacher_group, _ = Group.objects.get_or_create(name='Teacher')
    teacher_perms = [p for p in task_perms if p.codename != 'delete_task']
    # Allow teachers to view all tasks
    teacher_perms += [p for p in user_perms if p.codename == 'view_all_tasks']
    teacher_group.permissions.set(teacher_perms)

    # Student: only view_task
    student_group, _ = Group.objects.get_or_create(name='Student')
    student_perms = [p for p in task_perms if p.codename == 'view_task']
    student_group.permissions.set(student_perms)


def remove_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ('Admin', 'Teacher', 'Student'):
        Group.objects.filter(name=name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
