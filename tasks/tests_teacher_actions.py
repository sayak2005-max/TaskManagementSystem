from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Task
from django.utils import timezone


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
            'title': 'Ajax Task',
            'description': 'Created via AJAX',
            'status': 'Pending',
            'due_date': timezone.now().date().isoformat(),
        }
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json.get('success'))
        self.assertEqual(Task.objects.filter(title='Ajax Task').count(), 1)

    def test_assign_task_ajax(self):
        # teacher creates a task
        task = Task.objects.create(title='To Assign', created_by=self.teacher, status='Pending', description='x', due_date=timezone.now().date())
        self.client.login(username='teacher1', password='pass')
        url = reverse('assign_task')
        data = {'task_id': task.id, 'assigned_to': self.student.id}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json.get('success'))
        task.refresh_from_db()
        self.assertEqual(task.assigned_to, self.student)

    def test_student_update_status_ajax(self):
        # create a task assigned to student
        task = Task.objects.create(title='Student Task', created_by=self.teacher, assigned_to=self.student, status='Pending', description='x', due_date=timezone.now().date())
        self.client.login(username='student1', password='pass')
        url = reverse('update_task_status', args=[task.id])
        data = {'status': 'Completed'}
        response = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        json = response.json()
        self.assertTrue(json.get('success'))
        task.refresh_from_db()
        self.assertEqual(task.status, 'Completed')
