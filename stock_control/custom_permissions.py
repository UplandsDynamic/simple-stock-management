__Author__ = "Dan Bright, dan@uplandsdynamic.com"
__Copyright__ = "(c) Copyright 2021 Dan Bright"
__License__ = "GPL v3.0"
__Version__ = "Version 4.1"

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
