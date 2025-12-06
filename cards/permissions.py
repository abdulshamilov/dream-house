from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает создавать вопросы любому авторизованному пользователю,
    а редактировать/отвечать — только админам.
    """
    def has_permission(self, request, view):
        if view.action == 'create':  # создание вопроса
            return request.user.is_authenticated
        # для изменения (ответ) — только админ
        return request.user.is_staff
