from .models import Label

def user_labels(request):
    if request.user.is_authenticated:
        return {'user_labels': Label.objects.filter(user=request.user)}
    return {}
