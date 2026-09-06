def save_created_by(obj, request):
    if hasattr(obj, "created_by") and request.user.is_authenticated:
        obj.created_by = request.user
    return obj