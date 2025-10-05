from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class GuestAccessMiddleware:
    """
    Middleware to handle guest access to dashboard features gracefully.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that require authentication
        self.auth_required_urls = [
            '/dashboard/monitoring/',
            '/dashboard/predictions/',
            '/dashboard/locations/',
        ]
        
        # URLs that are guest-friendly
        self.guest_allowed_urls = [
            '/dashboard/',
            '/dashboard/guest-info/',
        ]

    def __call__(self, request):
        # Check if user is trying to access auth-required URLs as guest
        if not request.user.is_authenticated:
            for url in self.auth_required_urls:
                if request.path.startswith(url):
                    messages.info(request, 'Please sign in to access this feature.')
                    return redirect('users:login')
        
        response = self.get_response(request)
        return response