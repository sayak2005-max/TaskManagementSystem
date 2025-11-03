from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

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
from django.db import models
from django.conf import settings

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ], default='Pending')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title




class TaskFile(models.Model):   # 👈 THIS is what’s missing
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='task_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task.title} - {self.file.name}"
