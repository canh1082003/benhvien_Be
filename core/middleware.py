from django.shortcuts import redirect
from django.urls import resolve

class RedirectToReactMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Paths that SHOULD be handled by Django
        if path.startswith('/api/') or path.startswith('/admin/') or path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)
            
        # Everything else goes to React
        return redirect('http://localhost:5173' + path)
