from django.core.exceptions import PermissionDenied


def allowed_groups(*groups):
    def decorator(view_function):
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_function (request, *args, **kwargs)
            elif request.user.groups.filter(name__in=groups).exists():
                return view_function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return wrapper
    return decorator
