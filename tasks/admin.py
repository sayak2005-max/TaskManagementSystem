from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Task, TaskFile, CustomUser
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.db.models import Q


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        ("Roles", {"fields": ("role",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('list-students/', self.admin_site.admin_view(self.list_students_view), name='list-students'),
            path('list-teachers/', self.admin_site.admin_view(self.list_teachers_view), name='list-teachers'),
            path('manage-users/', self.admin_site.admin_view(self.manage_users_view), name='manage-users'),
            path('manage-roles/', self.admin_site.admin_view(self.manage_roles_view), name='manage-roles'),
            path('all-tasks/', self.admin_site.admin_view(self.all_tasks_view), name='all-tasks'),
            path('bulk-role-change/', self.admin_site.admin_view(self.bulk_role_change), name='bulk-role-change'),
        ]
        return custom_urls + urls

    @method_decorator(permission_required('tasks.add_customuser'))
    def manage_users_view(self, request):
        context = {
            'title': 'Manage Users',
            'users': CustomUser.objects.all().order_by('-date_joined'),
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/tasks/customuser/manage_users.html', context)

    @method_decorator(permission_required('tasks.change_customuser'))
    def manage_roles_view(self, request):
        context = {
            'title': 'Manage User Roles',
            'users': CustomUser.objects.all().order_by('role', 'username'),
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/tasks/customuser/manage_roles.html', context)

    @method_decorator(permission_required('tasks.view_task'))
    def all_tasks_view(self, request):
        context = {
            'title': 'All Tasks Overview',
            'tasks': Task.objects.all().select_related('created_by', 'assigned_to'),
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/tasks/customuser/all_tasks.html', context)

    @method_decorator(permission_required('tasks.change_customuser'))
    def bulk_role_change(self, request):
        if request.method == 'POST':
            user_ids = request.POST.getlist('user_ids')
            new_role = request.POST.get('new_role')
            if user_ids and new_role:
                CustomUser.objects.filter(id__in=user_ids).update(role=new_role)
                messages.success(request, f'Successfully updated roles for {len(user_ids)} users.')
        return redirect('admin:tasks_customuser_changelist')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Role Info', {'fields': ('role',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    
    def user_actions(self, obj):
        return format_html(
            '<a class="button" style="color: blue;" href="/admin/tasks/customuser/{}/change/">Edit</a>&nbsp;'
            '<a class="button" style="color: red;" href="/admin/tasks/customuser/{}/delete/">Delete</a>',
            obj.id, obj.id
        )
    user_actions.short_description = 'Actions'

    def list_students_view(self, request):
        context = {
            'students': CustomUser.objects.filter(role='Student').order_by('first_name', 'last_name'),
            'title': 'Student List',
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/tasks/customuser/student_list.html', context)

    def list_teachers_view(self, request):
        context = {
            'teachers': CustomUser.objects.filter(role='Teacher').order_by('first_name', 'last_name'),
            'title': 'Teacher List',
            **self.admin_site.each_context(request),
        }
        return render(request, 'admin/tasks/customuser/teacher_list.html', context)

    def add_to_teacher_group(self, request, queryset):
        group, _ = Group.objects.get_or_create(name='Teacher')
        for user in queryset:
            user.groups.add(group)
        messages.success(request, f'Added {queryset.count()} user(s) to Teacher group.')
    add_to_teacher_group.short_description = 'Add selected users to Teacher group'

    def add_to_student_group(self, request, queryset):
        group, _ = Group.objects.get_or_create(name='Student')
        for user in queryset:
            user.groups.add(group)
        messages.success(request, f'Added {queryset.count()} user(s) to Student group.')
    add_to_student_group.short_description = 'Add selected users to Student group'

    def remove_from_teacher_group(self, request, queryset):
        group = Group.objects.filter(name='Teacher').first()
        if not group:
            messages.warning(request, 'Teacher group does not exist.')
            return
        for user in queryset:
            user.groups.remove(group)
        messages.success(request, f'Removed {queryset.count()} user(s) from Teacher group.')
    remove_from_teacher_group.short_description = 'Remove selected users from Teacher group'

    def remove_from_student_group(self, request, queryset):
        group = Group.objects.filter(name='Student').first()
        if not group:
            messages.warning(request, 'Student group does not exist.')
            return
        for user in queryset:
            user.groups.remove(group)
        messages.success(request, f'Removed {queryset.count()} user(s) from Student group.')
    remove_from_student_group.short_description = 'Remove selected users from Student group'
   
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # ✅ Show all users if superuser
        if request.user.is_superuser:
            return qs
        # Otherwise show nothing (or you could filter)
        return qs.none()

    def has_add_permission(self, request):
        # ✅ Allow only Admins to add Teachers
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # ✅ Allow only Admins to delete Teachers
        return request.user.is_superuser


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'created_by', 'created_at', 'status', 'action_buttons')
    list_filter = ('status', 'created_at', 'created_by', 'assigned_to')
    search_fields = ('title', 'description', 'assigned_to__username', 'created_by__username')
    date_hierarchy = 'created_at'
    list_per_page = 20

    # Mark created_at as readonly instead of excluding it
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description')
        }),
        ('Assignment Details', {
            'fields': ('assigned_to', 'created_by', 'status', 'created_at')
        }),
    )

    # IMPORTANT FIX 🔥
    # Tell Django which admin handles this ForeignKey
    raw_id_fields = ('assigned_to', 'created_by')
    autocomplete_fields = ('assigned_to', 'created_by')

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="/admin/tasks/task/{}/change/">Edit</a>&nbsp;'
            '<a class="button" style="color: red;" href="/admin/tasks/task/{}/delete/">Delete</a>',
            obj.id, obj.id
        )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)


@admin.register(TaskFile)
class TaskFileAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('task__title',)
