from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Task
from django.utils import timezone
from datetime import date, timedelta


class TeacherActionsTest(TestCase):
    def setUp(self):
        # Create teacher and student users
        self.teacher = CustomUser.objects.create_user(username='teacher1', password='pass', role='Teacher')
        self.student = CustomUser.objects.create_user(username='student1', password='pass', role='Student')
        self.client = Client()

    def test_create_task_ajax(self):
        self.client.login(username='teacher1', password='pass')
        url = reverse('create_task')
        data = {
            'title': 'Test Task',
            'description': 'Test description',
            'assigned_to': self.student.id,
            'due_date': (date.today() + timedelta(days=7)).isoformat(),  # added line
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json.get('success'))
        self.assertEqual(Task.objects.filter(title='Test Task').count(), 1)

    def test_assign_task_ajax(self):
        # Log in as teacher
        self.client.login(username='teacher1', password='pass')

        # Create a task before assigning
        task = Task.objects.create(
            title="Sample Task",
            description="Test task for assignment",
            due_date=date.today() + timedelta(days=7),
            created_by=self.teacher
        )

        # Prepare the AJAX request data
        data = {
            'task_id': task.id,
            'student_id': self.student.id,
        }

        url = reverse('assign_task_ajax')

        # Send POST request as AJAX
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        # Assert response is successful
        self.assertEqual(response.status_code, 200)

    def test_student_update_status_ajax(self):
        # Create a task assigned to student
        task = Task.objects.create(
            title='Student Task',
            created_by=self.teacher,
            assigned_to=self.student,
            status='Pending',
            description='x',
            due_date=timezone.now().date()
        )
        self.client.login(username='student1', password='pass')
        url = reverse('update_task_status', args=[task.id])
        data = {'status': 'Completed'}
        response = self.client.post(
    reverse("student_update_status_ajax"),
    {"task_id": task.id, "status": "Completed"}
)

        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json.get('success'))
        task.refresh_from_db()
        self.assertEqual(task.status, 'Completed')
