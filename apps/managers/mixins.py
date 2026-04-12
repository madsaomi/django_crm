from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

class ManagerRequiredMixin(AccessMixin):
    """Verify that the current user is a superuser or an active manager."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
            
        if hasattr(request.user, 'manager') and request.user.manager.is_active:
            return super().dispatch(request, *args, **kwargs)
            
        raise PermissionDenied("Доступ запрещен. Требуются права Менеджера.")
