import uuid

from sqlalchemy.orm import Session

from app.models.worker import Worker


def create_worker(db: Session, business_id: uuid.UUID, **data):
    worker = Worker(business_id=business_id, **data)
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


def list_workers(
    db: Session,
    business_id: uuid.UUID,
    include_inactive: bool = False,
):
    query = db.query(Worker).filter(Worker.business_id == business_id)

    if not include_inactive:
        query = query.filter(Worker.is_active.is_(True))

    return query.order_by(Worker.first_name, Worker.last_name).all()


def get_worker(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
):
    return (
        db.query(Worker)
        .filter(
            Worker.business_id == business_id,
            Worker.id == worker_id,
        )
        .first()
    )


def update_worker(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
    **data,
):
    worker = get_worker(db, business_id, worker_id)

    if worker is None:
        return None

    for field, value in data.items():
        setattr(worker, field, value)

    db.commit()
    db.refresh(worker)
    return worker


def delete_worker(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
):
    worker = get_worker(db, business_id, worker_id)

    if worker is None:
        return False

    db.delete(worker)
    db.commit()
    return True
