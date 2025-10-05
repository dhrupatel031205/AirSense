from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def guest_allowed(view_func):
    """
    Decorator that allows both authenticated and guest users to access a view.
    Provides different functionality based on authentication status.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper

def authenticated_required(view_func):
    """
    Decorator that requires authentication and redirects guests to login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, 'Please sign in to access this feature.')
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper