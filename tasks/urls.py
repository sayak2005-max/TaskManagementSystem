# tasks/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    # ---------- Home ----------
    path("", views.home, name="home"),

    # ---------- Authentication ----------
    # Registration with OTP
    path("register/", views.register, name="register"),
    path(
        "register/verify-otp/",
        views.verify_registration_otp,
        name="register_verify_otp",
    ),

    # Login with OTP
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("logout/", views.logout_view, name="logout"),

    # ---------- Password Reset ----------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="tasks/password/password_reset.html",
            email_template_name="tasks/password/password_reset_email.html",
            subject_template_name="tasks/password/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="tasks/password/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="tasks/password/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="tasks/password/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

    # ---------- Dashboards ----------
    path("teacher_dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # ---------- Task Management ----------
    path("create-task/", views.create_task, name="create_task"),
    path("assign_task/", views.assign_task, name="assign_task"),
    path("upload_notes/", views.upload_notes, name="upload_notes"),
    path("update-task/<int:task_id>/", views.update_task, name="update_task"),
    path(
        "update-task-status/<int:task_id>/",
        views.update_task_status,
        name="update_task_status",
    ),
    path("delete-task/<int:task_id>/", views.delete_task, name="delete_task"),

    # AJAX endpoints
    path("ajax/create-task/", views.create_task_ajax, name="create_task_ajax"),
    path("ajax/assign-task/", views.assign_task_ajax, name="assign_task_ajax"),
    path(
        "student/update-status/",
        views.student_update_status_ajax,
        name="student_update_status_ajax",
    ),

    # ---------- Reports ----------
    path(
        "generate-task-report/",
        views.generate_task_report,
        name="generate_task_report",
    ),

    # ---------- Admin Controls ----------
    path("admin-panel/students/", views.admin_student_list, name="admin_student_list"),
    path("admin-panel/teachers/", views.admin_teacher_list, name="admin_teacher_list"),
    path("list-teachers/", views.list_teachers, name="list_teachers"),

    # ---------- User / Student Management ----------
    path("students/", views.student_list, name="student_list"),
    path("teacher/students/", views.student_list, name="teacher_student_list"),
    path("edit-student/<int:student_id>/", views.edit_student, name="edit_student"),
    path("delete-student/<int:student_id>/", views.delete_student, name="delete_student"),

    # Teacher’s task lists
    path("teacher/tasks/", views.teacher_tasks, name="teacher_tasks"),
    path("teacher/completed/", views.completed_tasks, name="completed_tasks"),
    path("teacher/pending/", views.pending_tasks, name="pending_tasks"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
