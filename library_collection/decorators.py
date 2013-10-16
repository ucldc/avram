from functools import wraps
from django.utils.decorators import available_attrs
from django.shortcuts import render

from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import user_passes_test

def user_passes_verification(test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return render(request, 
                template_name='library_collection/verification_required.html', 
                dictionary={
                    'user': request.user
                },
            )
            
        return _wrapped_view
    return decorator
    

def verification_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_verification(
        lambda u: u.is_active
    )
    
    if function:
        return actual_decorator(function)
    return actual_decorator
