from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

# ✅ Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'Admin'

    @property
    def is_teacher(self):
        return self.role == 'Teacher'

    @property
    def is_student(self):
        return self.role == 'Student'

    def can_manage_users(self):
        return self.is_admin or self.is_superuser

    def can_assign_roles(self):
        return self.is_admin or self.is_superuser

    def can_view_all_tasks(self):
        return self.is_admin or self.is_superuser

    class Meta:
        permissions = [
            ("manage_users", "Can manage user accounts"),
            ("assign_roles", "Can assign roles to users"),
            ("view_all_tasks", "Can view all tasks in the system"),
        ]


# ✅ Task Model
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed')
        ],
        default='Pending'
    )

    due_date = models.DateField(null=True, blank=True)  # ✅ FIX ADDED
    task_type = models.CharField(max_length=50, blank=True, null=True)  # NEW
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class NotesUpload(models.Model):
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='notes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notes by {self.uploaded_by.username} - {self.file.name}"

# ✅ TaskFile Model (for multiple file attachments, optional)
class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='task_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.file.name}"
