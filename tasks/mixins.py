from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class AdminRequiredMixin(UserPassesTestMixin):
    """Verify that the current user is an admin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'Admin'
    
    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("You must be an admin to access this page.")