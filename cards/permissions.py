from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает создавать вопросы любому авторизованному пользователю,
    а редактировать/отвечать — только админам.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff
