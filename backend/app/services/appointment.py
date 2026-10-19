import uuid

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.customer import Customer
from app.models.service import Service
from app.models.worker import Worker


ACTIVE_STATUSES = ("scheduled", "confirmed")


def validate_references(
    db: Session,
    business_id: uuid.UUID,
    customer_id: uuid.UUID,
    service_id: uuid.UUID,
    worker_id: uuid.UUID,
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == business_id,
    ).first()

    service = db.query(Service).filter(
        Service.id == service_id,
        Service.business_id == business_id,
        Service.is_active.is_(True),
    ).first()

    worker = db.query(Worker).filter(
        Worker.id == worker_id,
        Worker.business_id == business_id,
        Worker.is_active.is_(True),
    ).first()

    if not customer or not service or not worker:
        return False

    return True


def has_worker_conflict(
    db: Session,
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
    start_time,
    end_time,
    exclude_appointment_id=None,
):
    query = db.query(Appointment).filter(
        Appointment.business_id == business_id,
        Appointment.worker_id == worker_id,
        Appointment.status.in_(ACTIVE_STATUSES),
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )

    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)

    return query.first() is not None


def create_appointment(
    db: Session,
    business_id: uuid.UUID,
    **data,
):
    appointment = Appointment(business_id=business_id, **data)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def list_appointments(
    db: Session,
    business_id: uuid.UUID,
):
    return (
        db.query(Appointment)
        .filter(Appointment.business_id == business_id)
        .order_by(Appointment.start_time)
        .all()
    )


def get_appointment(
    db: Session,
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
):
    return db.query(Appointment).filter(
        Appointment.business_id == business_id,
        Appointment.id == appointment_id,
    ).first()


def update_appointment(
    db: Session,
    appointment: Appointment,
    **data,
):
    for field, value in data.items():
        setattr(appointment, field, value)

    db.commit()
    db.refresh(appointment)
    return appointment


def delete_appointment(
    db: Session,
    appointment: Appointment,
):
    db.delete(appointment)
    db.commit()
