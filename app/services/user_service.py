from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.role import Role
from app.models.college import College
from app.models.user_role import UserRole
from app.schemas.user_schema import UserCreate, UserUpdate
from datetime import datetime

# ======================
# GET USERS
# ======================
def get_users(db: Session, role_name: str = None):
    # pick a single active role per user (if a user has multiple roles, choose the one with the smallest role_id)
    role_subq = (
        db.query(
            UserRole.user_id.label("ur_user_id"),
            func.min(UserRole.role_id).label("ur_role_id"),
        )
        .filter(UserRole.status == 1)
        .group_by(UserRole.user_id)
        .subquery()
    )

    rows = (
        db.query(
            User.user_id,
            User.username.label("name"),
            User.email,
            User.phone,
            User.status,
            User.created_at,
            Role.role_id,
            Role.role_name,
            College.college_id,
            College.college_name,
        )
        .outerjoin(role_subq, role_subq.c.ur_user_id == User.user_id)
        .outerjoin(Role, Role.role_id == role_subq.c.ur_role_id)
        .join(College, College.college_id == User.college_id)
    )
    if role_name:
        rows = rows.filter(Role.role_name == role_name).all()
    else:
        rows = rows.all()
    

    result = []
    for r in rows:
        created_at = r.created_at.isoformat() if r.created_at else None
        result.append(
            {
                "user_id": r.user_id,
                "name": r.name,
                "email": r.email,
                "phone": r.phone,
                "role_id": r.role_id,
                "role_name": r.role_name,
                "college_id": r.college_id,
                "college_name": r.college_name,
                "status": "active" if r.status == 1 else "inactive",
                "created_at": created_at,
            }
        )

    return result


# ======================
# CREATE USER
# ======================
def create_user(db: Session, data: UserCreate):
    # validate role exists
    role = db.query(Role).filter(Role.role_id == data.role_id, Role.status == 1).first()
    if not role:
        return {"error": "Role not found or inactive"}
    # validate college exists
    college = db.query(College).filter(College.college_id == data.college_id, College.status == 1).first()
    if not college:
        return {"error": "College not found or inactive"}

    user = User(
        username=data.name,
        email=data.email,
        phone=data.phone,
        college_id=data.college_id,
        status=1 if data.status == "active" else 0,
        password_hash="TEMP_PASSWORD",  # later bcrypt
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # create user_role entry
    user_role = UserRole(user_id=user.user_id, role_id=data.role_id, status=1)
    db.add(user_role)
    db.commit()

    return {
        "user_id": user.user_id,
        "name": user.username,
        "email": user.email,
        "phone": user.phone,
        "role_id": role.role_id,
        "role_name": role.role_name,
        "college_id": user.college_id,
        "college_name": db.query(College.college_name).filter(College.college_id == user.college_id).scalar(),
        "status": "active" if user.status == 1 else "inactive",
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ======================
# UPDATE USER
# ======================
def update_user(db: Session, user_id: int, data: UserUpdate):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}
    # validate role exists
    role = db.query(Role).filter(Role.role_id == data.role_id, Role.status == 1).first()
    if not role:
        return {"error": "Role not found or inactive"}
    # validate college exists
    college = db.query(College).filter(College.college_id == data.college_id, College.status == 1).first()
    if not college:
        return {"error": "College not found or inactive"}

    # update user basic fields
    user.username = data.name
    user.email = data.email
    user.phone = data.phone
    user.college_id = data.college_id
    user.status = 1 if data.status == "active" else 0

    # update user roles: set provided role active, others inactive
    existing_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    found = False
    for ur in existing_roles:
        if ur.role_id == data.role_id:
            ur.status = 1
            found = True
        else:
            ur.status = 0

    if not found:
        db.add(UserRole(user_id=user_id, role_id=data.role_id, status=1))

    db.commit()

    return {
        "user_id": user.user_id,
        "name": user.username,
        "email": user.email,
        "phone": user.phone,
        "role_id": role.role_id,
        "role_name": role.role_name,
        "college_id": user.college_id,
        "college_name": db.query(College.college_name).filter(College.college_id == user.college_id).scalar(),
        "status": "active" if user.status == 1 else "inactive",
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ======================
# TOGGLE STATUS
# ======================
def toggle_user_status(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {"error": "User not found"}
    user.status = 0 if user.status == 1 else 1
    db.commit()

    return {
        "message": "User status updated",
        "status": "active" if user.status == 1 else "inactive",
    }


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return False

    # delete user roles first
    db.query(UserRole).filter(UserRole.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return True
