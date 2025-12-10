from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Task
from django.utils import timezone


class TeacherDashboardTests(TestCase):
    def setUp(self):
        self.teacher = CustomUser.objects.create_user(username='teacher1', password='pass1234', role='Teacher', email='t@example.com', first_name='T', last_name='One')
        self.student = CustomUser.objects.create_user(username='student1', password='pass1234', role='Student', email='s@example.com', first_name='S', last_name='One')

        self.task = Task.objects.create(
            title='Test Task',
            description='A test task',
            assigned_to=self.student,
            created_by=self.teacher,
            due_date=timezone.now().date(),
            status='Pending'
        )

        self.client = Client()

    def test_non_teacher_redirected(self):
        self.client.login(username='student1', password='pass1234')
        resp = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(resp.status_code, 302)

    def test_teacher_sees_dashboard(self):
        self.client.login(username='teacher1', password='pass1234')
        resp = self.client.get(reverse('teacher_dashboard'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        self.assertIn(str(1), content)
        self.assertIn('Test Task', content)

    def test_teacher_cannot_delete_other_teacher_task(self):
        other_teacher = CustomUser.objects.create_user(username='teacher2', password='pass1234', role='Teacher')
        other_task = Task.objects.create(
            title='Other Task',
            description='Other',
            assigned_to=self.student,
            created_by=other_teacher,
            due_date=timezone.now().date(),
            status='Pending'
        )

        self.client.login(username='teacher1', password='pass1234')
        resp = self.client.get(reverse('delete_task', args=[other_task.id]), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Task.objects.filter(id=other_task.id).exists())
