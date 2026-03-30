from rest_framework.permissions import BasePermission


class BaseRolePermission(BasePermission):
    """
    Base permission to check authentication and profile existence.
    """

    required_role = None

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if not hasattr(user, "profile"):
            return False

        if self.required_role and user.profile.role != self.required_role:
            return False

        return True


class IsFaculty(BaseRolePermission):
    required_role = "FACULTY"


class IsStudent(BaseRolePermission):
    required_role = "STUDENT"


class IsStudentAndOwner(IsStudent):

    def has_object_permission(self, request, view, obj):
        return obj.student.user == request.user