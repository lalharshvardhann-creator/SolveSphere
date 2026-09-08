from enum import Enum


class UserRole(str, Enum):
    CITIZEN = "citizen"
    UNIVERSITY = "university"
    FACULTY = "faculty"
    STUDENT = "student"
    INDUSTRY = "industry"
    GOVERNMENT_ADMIN = "government_admin"


VALID_ROLES = {role.value for role in UserRole}
