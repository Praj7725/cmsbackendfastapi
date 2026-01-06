from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from sqlalchemy.orm import Session
import hashlib
import os
from datetime import datetime, timedelta

try:
    from jose import jwt, JWTError
    _JOSE_AVAILABLE = True
    _USING_PYJWT = False
except Exception:
    try:
        import jwt
        from jwt.exceptions import PyJWTError as JWTError
        _JOSE_AVAILABLE = True
        _USING_PYJWT = True
    except Exception:
        jwt = None
        JWTError = Exception
        _JOSE_AVAILABLE = False
        _USING_PYJWT = False

from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.database import SessionLocal
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.models.college import College

# ============================================================================
# CONFIGURATION
# ============================================================================

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Bcrypt password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Router setup
router = APIRouter(prefix="/auth", tags=["Auth"])

# Constants
MAX_PASSWORD_LENGTH = 72  # Bcrypt's hard limit in bytes


# ============================================================================
# DATABASE DEPENDENCY
# ============================================================================

def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        """Validate password doesn't exceed bcrypt's limit"""
        if len(v.encode('utf-8')) > MAX_PASSWORD_LENGTH:
            raise ValueError(f'Password cannot exceed {MAX_PASSWORD_LENGTH} bytes')
        return v


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict
    permissions: List[str]


class RefreshResponse(BaseModel):
    access_token: str


# ============================================================================
# PASSWORD UTILITIES
# ============================================================================

def preprocess_password(password: str) -> str:
    """
    Preprocess password to handle bcrypt's 72-byte limit.
    For passwords > 72 bytes, use SHA256 hash to reduce size.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > MAX_PASSWORD_LENGTH:
        # Hash long passwords with SHA256 to fit bcrypt's limit
        return hashlib.sha256(password_bytes).hexdigest()
    return password


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with preprocessing for long passwords.
    Use this when creating or updating user passwords.
    """
    processed = preprocess_password(password)
    return pwd_context.hash(processed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    Handles bcrypt's 72-byte limit and various error cases gracefully.
    """
    try:
        # Preprocess password (handles > 72 bytes)
        processed = preprocess_password(plain_password)
        return pwd_context.verify(processed, hashed_password)
    except UnknownHashError:
        # Invalid hash format
        return False
    except ValueError as e:
        # Bcrypt-specific errors (shouldn't happen with preprocessing, but just in case)
        if "72 bytes" in str(e):
            return False
        raise
    except Exception:
        # Any other unexpected errors
        return False


# ============================================================================
# JWT TOKEN UTILITIES
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if not _JOSE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT library not available. Install python-jose[cryptography] or PyJWT"
        )
    
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    
    if _USING_PYJWT:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    if not _JOSE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT library not available. Install python-jose[cryptography] or PyJWT"
        )
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    if _USING_PYJWT:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    if not _JOSE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT library not available. Install python-jose[cryptography] or PyJWT"
        )
    
    try:
        if _USING_PYJWT:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        else:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ============================================================================
# USER & ROLE UTILITIES
# ============================================================================

def load_user_role(db: Session, user_id: int) -> Optional[Role]:
    """Load the primary active role for a user"""
    user_role = (
        db.query(UserRole)
        .filter(UserRole.user_id == user_id, UserRole.status == 1)
        .order_by(UserRole.role_id)
        .first()
    )
    
    if not user_role:
        return None
    
    role = (
        db.query(Role)
        .filter(Role.role_id == user_role.role_id, Role.status == 1)
        .first()
    )
    
    return role


def load_permissions_for_user(db: Session, user_id: int) -> List[str]:
    """Load all permissions for a user based on their roles"""
    # Get all active role IDs for the user
    role_ids = [
        r.role_id for r in 
        db.query(UserRole.role_id)
        .filter(UserRole.user_id == user_id, UserRole.status == 1)
        .all()
    ]
    
    if not role_ids:
        return []
    
    # Get all permissions for those roles
    permissions = (
        db.query(Permission.permission_code)
        .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
        .filter(
            RolePermission.role_id.in_(role_ids),
            RolePermission.status == 1,
            Permission.status == 1
        )
        .all()
    )
    
    # Return unique permission codes
    return list({p[0] for p in permissions})


def is_super_admin(db: Session, role_id: Optional[int]) -> bool:
    """Check if a role is Super Admin"""
    if not role_id:
        return False
    
    role = db.query(Role).filter(Role.role_id == role_id, Role.status == 1).first()
    return role and role.role_name and role.role_name.lower() == "super admin"


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access/refresh tokens.
    
    - **email**: User's email address
    - **password**: User's password (max 72 bytes for bcrypt)
    """
    
    # Find user by email
    user = (
        db.query(User)
        .filter(User.email == data.email, User.status == 1)
        .first()
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Load user's role and permissions
    role = load_user_role(db, user.user_id)
    permissions = load_permissions_for_user(db, user.user_id)
    
    # Create token payload
    token_payload = {
        "user_id": user.user_id,
        "role_id": role.role_id if role else None,
        "college_id": user.college_id,
        "permissions": permissions,
    }
    
    # Generate tokens
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    
    # Get college information
    college = None
    if user.college_id:
        college = (
            db.query(College)
            .filter(College.college_id == user.college_id)
            .first()
        )
    
    # Return response
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "name": user.username,
            "email": user.email,
            "role_id": role.role_id if role else None,
            "role_name": role.role_name if role else None,
            "college_id": user.college_id,
            "college_name": college.college_name if college else None,
        },
        "permissions": permissions,
    }


@router.post("/refresh", response_model=RefreshResponse)
def refresh_access_token(data: RefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh an access token using a valid refresh token.
    
    - **refresh_token**: Valid refresh token obtained from login
    """
    
    # Decode refresh token
    payload = decode_token(data.refresh_token)
    
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Optionally: Reload permissions from database for fresh data
    user_id = payload.get("user_id")
    if user_id:
        permissions = load_permissions_for_user(db, user_id)
        payload["permissions"] = permissions
    
    # Create new access token
    token_payload = {
        "user_id": payload.get("user_id"),
        "role_id": payload.get("role_id"),
        "college_id": payload.get("college_id"),
        "permissions": payload.get("permissions", []),
    }
    
    access_token = create_access_token(token_payload)
    
    return {"access_token": access_token}


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal).
    Server-side token invalidation would require a token blacklist.
    """
    return {"message": "Logged out successfully. Remove tokens from client storage."}


# ============================================================================
# AUTHORIZATION DEPENDENCY
# ============================================================================

def require_permissions(permission_codes: List[str]):
    """
    Dependency factory to check if user has required permissions.
    Super Admin bypasses all permission checks.
    
    Usage:
        @router.get("/protected", dependencies=[Depends(require_permissions(["read:users"]))])
    """
    
    def permission_checker(request: Request, db: Session = Depends(get_db)):
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        token = auth_header.split(" ", 1)[1]
        
        # Decode token
        payload = decode_token(token)
        
        # Verify it's an access token
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        role_id = payload.get("role_id")
        
        # Super Admin bypass
        if is_super_admin(db, role_id):
            return payload
        
        # Check permissions
        user_permissions = payload.get("permissions", []) or []
        
        if not all(perm in user_permissions for perm in permission_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return payload
    
    return permission_checker


def get_current_user(request: Request, db: Session = Depends(get_db)) -> dict:
    """
    Dependency to get current authenticated user from token.
    
    Usage:
        @router.get("/me")
        def get_me(current_user: dict = Depends(get_current_user)):
            return current_user
    """
    
    # Extract token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = auth_header.split(" ", 1)[1]
    
    # Decode and return payload
    payload = decode_token(token)
    
    # Verify it's an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    return payload


# ============================================================================
# UTILITY ENDPOINT FOR TESTING
# ============================================================================

@router.get("/me")
def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current authenticated user's information.
    Useful for testing authentication and getting user details.
    """
    
    user_id = current_user.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id, User.status == 1).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = load_user_role(db, user_id)
    college = None
    if user.college_id:
        college = db.query(College).filter(College.college_id == user.college_id).first()
    
    return {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role_id": role.role_id if role else None,
        "role_name": role.role_name if role else None,
        "college_id": user.college_id,
        "college_name": college.college_name if college else None,
        "permissions": current_user.get("permissions", []),
        "is_super_admin": is_super_admin(db, current_user.get("role_id"))
    }