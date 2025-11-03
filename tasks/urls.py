from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ---------- Home ----------
    path('', views.home, name='home'),

    # ---------- Authentication ----------
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ---------- Password Reset ----------
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='tasks/password/password_reset.html',
            email_template_name='tasks/password/password_reset_email.html',
            subject_template_name='tasks/password/password_reset_subject.txt'
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='tasks/password/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='tasks/password/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='tasks/password/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # ---------- Dashboards ----------
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ---------- Debug & Reports ----------
    path('debug/csrf/', views.debug_csrf, name='debug_csrf'),
    path('list-teachers/', views.list_teachers, name='list_teachers'),
    path('list-students/', views.list_students, name='list_students'),
    path('generate-task-report/', views.generate_task_report, name='generate_task_report'),

    # ---------- Admin User Management ----------
    path('admin/users/', views.admin_user_list, name='admin_user_list'),

    # ---------- Task Management ----------
    path('create-task/', views.create_task_ajax, name='create_task'),
    path('assign-task-ajax/', views.assign_task_ajax, name='assign_task_ajax'),
    path('update-task/<int:task_id>/', views.update_task, name='update_task'),
    path('update-task-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('delete-task/<int:task_id>/', views.delete_task, name='delete_task'),

    # ---------- Teacher Views ----------
    path('teacher/tasks/', views.teacher_tasks, name='teacher_tasks'),
    path('teacher/completed/', views.completed_tasks, name='completed_tasks'),
    path('teacher/pending/', views.pending_tasks, name='pending_tasks'),
    path('teacher/students/', views.student_list, name='student_list'),

    # ---------- User Management ----------
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
]
