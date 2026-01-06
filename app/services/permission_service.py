from sqlalchemy.orm import Session
from app.models.permission import Permission


def get_permissions(db: Session):
	"""Return active permissions as a list of Permission ORM objects."""
	return db.query(Permission).filter(Permission.status == 1).all()


def get_permission_by_code(db: Session, code: str):
	return db.query(Permission).filter(Permission.permission_code == code).first()
