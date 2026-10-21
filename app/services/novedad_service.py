from sqlalchemy.orm import Session
from app.models.novedad import Novedad
from datetime import datetime, timedelta


def create_novedad(db: Session, module_name: str | None, message: str, days_to_expire: int = 5):
    """Create a novedad. module_name is accepted for compatibility but
    the system treats novedades as global; we store a default value if None."""
    expires_at = datetime.now() + timedelta(days=days_to_expire)
    stored_module = module_name or "System"
    db_novedad = Novedad(module_name=stored_module, message=message, expires_at=expires_at)
    db.add(db_novedad)
    db.commit()
    db.refresh(db_novedad)
    return db_novedad


def get_novedad(db: Session, novedad_id: int):
    return db.query(Novedad).filter(Novedad.id == novedad_id).first()


def get_novedades_by_module(db: Session, module_name: str | None):
    """Backward-compatible: ignore module_name and return all novedades ordered by date."""
    return db.query(Novedad).order_by(Novedad.created_at.desc()).all()


def get_active_novedades_by_module(db: Session, module_name: str | None):
    """Backward-compatible: ignore module_name and return all active novedades."""
    return db.query(Novedad).filter(
        Novedad.expires_at > datetime.now()
    ).order_by(Novedad.created_at.desc()).all()


def get_active_novedades(db: Session):
    return get_active_novedades_by_module(db, None)


def update_novedad(db: Session, novedad_id: int, message: str):
    db_novedad = db.query(Novedad).filter(Novedad.id == novedad_id).first()
    if db_novedad:
        db_novedad.message = message
        db.commit()
        db.refresh(db_novedad)
    return db_novedad


def delete_novedad(db: Session, novedad_id: int):
    db_novedad = db.query(Novedad).filter(Novedad.id == novedad_id).first()
    if db_novedad:
        db.delete(db_novedad)
        db.commit()
    return db_novedad


def delete_expired_novedades(db: Session):
    expired_novedades = db.query(Novedad).filter(Novedad.expires_at <= datetime.now()).all()
    for novedad in expired_novedades:
        db.delete(novedad)
    db.commit()
    return len(expired_novedades)
