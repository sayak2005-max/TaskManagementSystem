from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponseRedirect
from functools import wraps
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv
from .models import Task, CustomUser
from .forms import TaskForm, RegisterForm, StudentTaskForm
from django.views.decorators.http import require_POST
from .mixins import AdminRequiredMixin
from django.http import JsonResponse
from django.middleware.csrf import get_token
import logging
from django.conf import settings
from django.contrib.auth.models import Group
from .forms import TaskAssignForm 

logger = logging.getLogger(__name__)

# Rate limiting decorator
def rate_limit(limit=20, per=60):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.session.session_key:
                request.session.create()
                
            cache_key = f'rate_limit_{request.session.session_key}'
            requests = cache.get(cache_key, [])
            now = datetime.now()
            
            # Filter out old requests
            requests = [time for time in requests if time > now - timedelta(seconds=per)]
            
            if len(requests) >= limit:
                messages.warning(request, 'Please slow down. Too many requests.')
                return HttpResponseRedirect(request.path)
                
            requests.append(now)
            cache.set(cache_key, requests, per)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# ---------- Home ----------
@rate_limit(limit=20, per=60)  # 20 requests per minute
@never_cache
def home(request):
    response = render(request, 'tasks/home.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def get_teacher_dashboard_context(request):
    """Helper function to get the context data for teacher dashboard"""
    # Get all students
    students = CustomUser.objects.filter(role='Student').order_by('first_name', 'last_name')
    
    # Get tasks created by this teacher
    teacher_tasks = Task.objects.filter(created_by=request.user)
    
    # Get task statistics
    task_stats = {
        'total_tasks': teacher_tasks.count(),
        'completed_tasks': teacher_tasks.filter(status='Completed').count(),
        'pending_tasks': teacher_tasks.filter(status='Pending').count(),
        'total_students': students.count(),
    }
    
    # Get tasks due today
    today = timezone.now().date()
    tasks_due_today = teacher_tasks.filter(due_date=today)
    
    return {
        'students': students,
        'stats': {
            'total_tasks': task_stats['total_tasks'],
            'completed': task_stats['completed_tasks'],
            'in_progress': task_stats['pending_tasks'],
            'pending': task_stats['pending_tasks'],
            'progress': round((task_stats['completed_tasks'] / task_stats['total_tasks']) * 100) if task_stats['total_tasks'] > 0 else 0,
            'total_students': students.count(),
        },
        'tasks': teacher_tasks,
        'create_form': TaskForm(),
        'tasks_due_today': tasks_due_today,
        'teacher': request.user,
    }

@login_required
def teacher_dashboard(request):
    # Only show data for the logged-in teacher
    teacher = request.user

    # Fetch tasks created by this teacher
    total_tasks = Task.objects.filter(created_by=teacher).count()
    completed_tasks = Task.objects.filter(created_by=teacher, status='Completed').count()
    pending_tasks = Task.objects.filter(created_by=teacher, status='Pending').count()

    # Fetch all students
    students = CustomUser.objects.filter(role='Student')
    total_students = students.count()

    context = {
        'user': teacher,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'total_students': total_students,
        'students': students[:5],  # show top 5 students in dashboard list
    }

    return render(request, 'tasks/teacher_dashboard.html', context)

# ---------- Authentication ----------
@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        # Debugging: log incoming CSRF cookie and posted token when running in DEBUG
        cookie_val = request.COOKIES.get('csrftoken') or request.COOKIES.get('CSRF_COOKIE')
        posted_token = request.POST.get('csrfmiddlewaretoken')
        logger.debug("register POST: cookie_csrf=%s posted_csrf=%s user_agent=%s", cookie_val, posted_token, request.META.get('HTTP_USER_AGENT'))

        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()
            # Add user to the matching role group if it exists
            try:
                role_name = form.cleaned_data.get('role')
                if role_name:
                    group = Group.objects.filter(name=role_name).first()
                    if group:
                        user.groups.add(group)
            except Exception:
                logger.exception('Failed to assign group to new user')
            messages.success(request, 'Registration successful! Please login with your credentials.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

@rate_limit(limit=5, per=60)  # 5 login attempts per minute
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return render(request, 'tasks/login.html')
            
        # Get login attempts from cache
        attempts_key = f'login_attempts_{username}'
        attempts = cache.get(attempts_key, 0)
        
        if attempts >= 5:  # Limit login attempts
            messages.error(request, 'Too many login attempts. Please try again later.')
            return render(request, 'tasks/login.html')
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Clear login attempts on successful login
                cache.delete(attempts_key)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect based on role
                if user.role == 'Teacher':
                    return redirect('teacher_dashboard')
                elif user.role == 'Student':
                    return redirect('student_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            # Increment login attempts
            cache.set(attempts_key, attempts + 1, 300)  # Reset after 5 minutes
            messages.error(request, 'Invalid username or password.')
            
    response = render(request, 'tasks/login.html')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
@rate_limit(limit=10, per=60)
def logout_view(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
@staff_member_required
def admin_dashboard(request):
    # Get current date and a week ago date
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Gather all statistics
    stats = {
        'total_users': CustomUser.objects.count(),
        'total_tasks': Task.objects.count(),
        'completed_tasks': Task.objects.filter(status='Completed').count(),
        'pending_tasks': Task.objects.filter(status='Pending').count(),
        'total_teachers': CustomUser.objects.filter(role='Teacher').count(),
        'total_students': CustomUser.objects.filter(role='Student').count(),
        'tasks_due_today': Task.objects.filter(due_date=today, status='Pending').count(),
        'new_tasks_this_week': Task.objects.filter(created_at__gte=week_ago).count(),
    }

    context = {
        'stats': stats,
        'today': today,
        'week_ago': week_ago,
    }
    
    return render(request, 'tasks/admin_dashboard.html', context)


@login_required
@staff_member_required
def debug_csrf(request):
    """Debug endpoint (local only) that returns CSRF cookie and server token.

    Use this to verify the cookie the browser holds (csrftoken) and the
    server-generated CSRF token match. Only available to staff users.
    """
    # cookie value (may be None)
    cookie_val = request.COOKIES.get('csrftoken') or request.COOKIES.get('CSRF_COOKIE')
    server_token = get_token(request)

    # Log for convenience
    logger.debug("debug_csrf: cookie=%s server_token=%s", cookie_val, server_token)

    return JsonResponse({
        'cookie_csrf': cookie_val,
        'server_csrf_token': server_token,
        'user': request.user.username,
    })

@login_required
@staff_member_required
def generate_task_report(request):
    if request.method == 'POST':
        date_range = request.POST.get('date_range', 'week')
        report_type = request.POST.get('report_type', 'summary')
        
        today = timezone.now().date()
        
        # Determine date range
        if date_range == 'week':
            start_date = today - timedelta(days=7)
        elif date_range == 'month':
            start_date = today - timedelta(days=30)
        elif date_range == 'quarter':
            start_date = today - timedelta(days=90)
        else:  # year
            start_date = today - timedelta(days=365)
            
        # Get tasks within date range
        tasks = Task.objects.filter(created_at__date__gte=start_date)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="task_report_{date_range}_{today}.csv"'
        
        writer = csv.writer(response)
        
        if report_type == 'summary':
            # Write summary report
            writer.writerow(['Report Type', 'Summary'])
            writer.writerow(['Date Range', f'{start_date} to {today}'])
            writer.writerow(['Total Tasks', tasks.count()])
            writer.writerow(['Completed Tasks', tasks.filter(status='Completed').count()])
            writer.writerow(['Pending Tasks', tasks.filter(status='Pending').count()])
            
            # Task distribution by role
            writer.writerow([])
            writer.writerow(['Tasks by Role'])
            tasks_by_role = tasks.values('created_by__role').annotate(count=Count('id'))
            for role_data in tasks_by_role:
                writer.writerow([role_data['created_by__role'], role_data['count']])
                
        else:  # detailed report
            # Write detailed report
            writer.writerow(['Title', 'Description', 'Created By', 'Assigned To', 'Due Date', 'Status', 'Created At'])
            for task in tasks:
                writer.writerow([
                    task.title,
                    task.description[:100],  # Truncate long descriptions
                    f"{task.created_by.get_full_name()} ({task.created_by.role})",
                    f"{task.assigned_to.get_full_name()} ({task.assigned_to.role})",
                    task.due_date,
                    task.status,
                    task.created_at.date()
                ])
                
        return response
        
    return redirect('admin_dashboard')

@login_required
@staff_member_required
def list_teachers(request):
    teachers = CustomUser.objects.filter(role='Teacher').order_by('username')
    return render(request, 'tasks/list_teachers.html', {'teachers': teachers})

@login_required
@staff_member_required
def list_students(request):
    students = CustomUser.objects.filter(role='Student').order_by('username')
    return render(request, 'tasks/list_students.html', {'students': students})

# ---------- Dashboards ----------

@login_required
def student_dashboard(request):
    # Only show tasks assigned to the logged-in student
    tasks = Task.objects.filter(assigned_to=request.user)

    # Count summary
    total_assigned = tasks.count()
    completed_count = tasks.filter(status='Completed').count()
    in_progress_count = tasks.filter(status='In Progress').count()
    pending_count = tasks.filter(status='Pending').count()

    context = {
        'tasks': tasks,
        'total_assigned': total_assigned,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'pending_count': pending_count,
    }

    return render(request, 'tasks/student_dashboard.html', context)

# ---------- Task CRUD ----------
@login_required
def create_task(request):
    # Allow Teachers and Admins to create tasks
    if request.user.role not in ['Teacher', 'Admin']:
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('teacher_dashboard')
    else:
        form = TaskForm()

    return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def assign_task(request):
    if request.method == 'POST':
        form = TaskAssignForm(request.POST)
        if form.is_valid():
            task = form.cleaned_data['task']
            student = form.cleaned_data['assigned_to']
            task.assigned_to = student
            task.save()
            messages.success(request, f'Task "{task.title}" assigned successfully!')
            return redirect('teacher_dashboard')
    else:
        form = TaskAssignForm()

    return render(request, 'tasks/assign_task.html', {'form': form})


@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # Only allow the creator or admins to update
    if not (request.user == task.created_by or request.user.is_superuser or getattr(request.user, 'role', None) == 'Admin'):
        messages.error(request, 'You do not have permission to edit this task.')
        return redirect('teacher_dashboard')
    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('teacher_dashboard')
    return render(request, 'tasks/update_task.html', {'form': form})

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    # Only allow the creator or admins to delete
    if not (request.user == task.created_by or request.user.is_superuser or getattr(request.user, 'role', None) == 'Admin'):
        messages.error(request, 'You do not have permission to delete this task.')
        return redirect('teacher_dashboard')
    task.delete()
    return redirect('teacher_dashboard')


@login_required
def update_task_status(request, task_id):
    """Allow the assigned student to update only the status of their assigned task.

    Accepts POST (regular or AJAX). Returns JSON on AJAX, otherwise redirects back to student_dashboard.
    """
    task = get_object_or_404(Task, id=task_id)

    # Only the assigned student can update their task status
    if task.assigned_to != request.user:
        messages.error(request, 'You do not have permission to update this task.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'permission_denied'}, status=403)
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'status': task.status})
            messages.success(request, 'Task status updated.')
            return redirect('student_dashboard')
        else:
            # Return JSON errors for AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
            # On non-AJAX, re-render student dashboard with form errors (simple approach)
            tasks = Task.objects.filter(assigned_to=request.user)
            stats = {
                'total_assigned': tasks.count(),
                'completed': tasks.filter(status='Completed').count(),
                'in_progress': tasks.filter(status='In Progress').count(),
                'pending': tasks.filter(status='Pending').count(),
            }
            return render(request, 'tasks/student_dashboard.html', {
                'tasks': tasks,
                'stats': stats,
                'status_form': form,
            })

    return redirect('student_dashboard')

@login_required
def admin_user_list(request):
    if request.user.role == 'Admin' or request.user.is_superuser:
        users = CustomUser.objects.all()
        return render(request, 'tasks/admin_user_list.html', {'users': users})
    else:
        return redirect('home')

@rate_limit(limit=5, per=60)
@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        selected_role = request.POST.get('role')  # Get role from form
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on role
            if user.role == 'Admin':
                return redirect('admin_dashboard')
            elif user.role == 'Teacher':
                return redirect('teacher_dashboard')
            else:
                return redirect('student_dashboard')
        elif selected_role:
                messages.error(request, f"⚠️ You selected '{selected_role}', but your account type is '{user.role}'.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'tasks/login.html')

@login_required
def edit_user(request, user_id):
    if request.user.role != 'Teacher':
        messages.error(request, "Only teachers can edit student details.")
        return redirect('teacher_dashboard')

    student = get_object_or_404(CustomUser, id=user_id, role='Student')

    if request.method == 'POST':
        form = RegisterForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.username}'s profile updated successfully!")
            return redirect('teacher_dashboard')
    else:
        form = RegisterForm(instance=student)

    return render(request, 'tasks/edit_user.html', {'form': form, 'student': student})


@login_required
def delete_user(request, user_id):
    if request.user.role != 'Teacher':
        messages.error(request, "Only teachers can delete students.")
        return redirect('teacher_dashboard')

    student = get_object_or_404(CustomUser, id=user_id, role='Student')
    if request.method == 'POST':
        student.delete()
        messages.success(request, f"Student '{student.username}' deleted successfully!")
        return redirect('teacher_dashboard')

    return redirect('teacher_dashboard')

@login_required
def teacher_tasks(request):
    tasks = Task.objects.filter(created_by=request.user)
    return render(request, 'tasks/teacher_tasks.html', {'tasks': tasks})

@login_required
def completed_tasks(request):
    tasks = Task.objects.filter(created_by=request.user, status='Completed')
    return render(request, 'tasks/completed_tasks.html', {'tasks': tasks})

@login_required
def pending_tasks(request):
    tasks = Task.objects.filter(created_by=request.user, status='Pending')
    return render(request, 'tasks/pending_tasks.html', {'tasks': tasks})

@login_required
def student_list(request):
    students = CustomUser.objects.filter(role='Student')
    return render(request, 'tasks/student_list.html', {'students': students})
