from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Task, TaskFile, CustomUser
from django.contrib.auth import get_user_model

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        # Use a single, clear save implementation. UserCreationForm
        # already takes care of setting the password fields.
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        # role is set by the view normally, but accept from cleaned_data if present
        role = self.cleaned_data.get('role')
        if role:
            user.role = role
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


User = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
         model = Task
         fields = "__all__"   
     
         widgets = {
            "created_at": forms.DateTimeInput(attrs={"type": "datetime-local"})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        # show only students to assign
        self.fields['assigned_to'].queryset = User.objects.filter(role='Student')

class StudentTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields =  ['title', 'description', 'attachment',]
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-green-500 outline-none'
            }),
        }

class TaskFileForm(forms.ModelForm):
    class Meta:
        model = TaskFile
        fields = ['file']

class TaskAssignForm(forms.Form):
    task = forms.ModelChoiceField(
        queryset=Task.objects.all(),
        label="Select Task"
    )
    assigned_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='Student'),
        label="Assign To (Student)"
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                "class": "form-control",
                "placeholder": field.label,
            })    