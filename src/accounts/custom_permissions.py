__Author__ = """By:  Aninstance
www.githup.com/Aninstance/simple-stock-management"""
__Copyright__ = "Copyright (c) 2021 Aninstance"
__Version__ = "Version 1.0"

from rest_framework import permissions


class AccessPermissions(permissions.BasePermission):
    """
    Custom permission to only allow staff or superusers to access api
    """

    def has_permission(self, request, view):
        # handles entire API
        return request.user.is_authenticated and request.user.is_staff  # by default, allow all authenticated, if staff

    def has_object_permission(self, request, view, obj):
        # handles actions on objects
        return request.user.is_staff  # staff only
