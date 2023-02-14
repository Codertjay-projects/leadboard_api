from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class StaffAndLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an organisor."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser or not request.user.is_staff:
            return redirect("/")
        return super().dispatch(request, *args, **kwargs)
