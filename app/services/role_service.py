from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole

def get_roles_with_permissions(db: Session, college_id: int):
    roles = db.query(Role).filter(Role.college_id == college_id).all()
    result = []

    for role in roles:
        permissions = (
            db.query(Permission.permission_code)
            .join(RolePermission, Permission.permission_id == RolePermission.permission_id)
            .filter(
                RolePermission.role_id == role.role_id,
                RolePermission.status == 1
            )
            .all()
        )

        users_count = (
            db.query(UserRole)
            .filter(UserRole.role_id == role.role_id, UserRole.status == 1)
            .count()
        )

        result.append({
            "id": role.role_id,
            "name": role.role_name,
            "description": role.description,
            "usersCount": users_count,
            "permissions": [p[0] for p in permissions]
        })

    return result


def create_role(db: Session, college_id: int, name: str, description: str = None):
    role = Role(
        college_id=college_id,
        role_code=name.upper().replace(" ", "_"),
        role_name=name,
        description=description
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
