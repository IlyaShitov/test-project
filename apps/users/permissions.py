from rest_framework.permissions import BasePermission


class UserViewSetPermission(BasePermission):

    def has_permission(self, request, view):

        if view.action == 'money_transfer':
            return request.user.has_perm('users.can_money_transfer')

        if view.action in ('list', 'retrieve', 'metadata'):
            return request.user.has_perm('users.view_user')
