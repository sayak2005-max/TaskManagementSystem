from django.contrib import admin
from django.urls import path, include

# Import views
from tasks.admin_view import admin_teacher_list, admin_student_list

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Main app URLs
    path('', include('tasks.urls')),
]
