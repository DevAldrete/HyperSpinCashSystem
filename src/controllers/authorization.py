from loguru import logger
from models.user import Role


class AuthorizationController:
    def __init__(self):
        self.roles = Role

    def has_access(self, user_role: Role, required_role: Role) -> bool:
        """Check if a user has the required role for access."""
        role_hierarchy = {
            Role.ADMIN: 2,
            Role.USER: 1,
        }
        return role_hierarchy[user_role] >= role_hierarchy[required_role]
    
    def assign_role(self, user, role: Role):
        """Assign a role to a user."""
        user.role = role
        return user
    
    def degrade_role_from_admin(self, user):
        """Demote an admin user to a regular user."""
        if user.role == Role.ADMIN:
            user.role = Role.USER
        else:
            logger.warning(f"User {user} is not an admin and cannot be degraded. Already an {user.role}")
            
        return user

