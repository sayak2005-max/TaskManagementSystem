from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

# ---------------------------
# STUDENT LIST PAGE
# ---------------------------
@staff_member_required
def admin_student_list(request):
    students = CustomUser.objects.filter(role="Student")
    return render(request, "admin/student_list.html", {
        "users": students,
        "title": "Student List",
        "simple": True,
    })


# ---------------------------
# TEACHER LIST PAGE
# ---------------------------
@staff_member_required
def admin_teacher_list(request):
    teachers = CustomUser.objects.filter(role="Teacher")
    return render(request, "admin/teacher_list.html", {
        "users": teachers,
        "title": "Teacher List",
        "simple": True,
    })
