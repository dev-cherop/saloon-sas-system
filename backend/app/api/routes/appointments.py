import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
)
from app.services.appointment import (
    create_appointment,
    delete_appointment,
    get_appointment,
    has_worker_conflict,
    list_appointments,
    update_appointment,
    validate_references,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/appointments",
    tags=["Appointments"],
)


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment_endpoint(
    business_id: uuid.UUID,
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("appointments:create")),
):
    data = payload.model_dump()

    if not validate_references(
        db, business_id,
        data["customer_id"], data["service_id"], data["worker_id"],
    ):
        raise HTTPException(status_code=400, detail="Invalid customer, service, or worker")

    if data["status"] in ("scheduled", "confirmed") and has_worker_conflict(
        db, business_id, data["worker_id"], data["start_time"], data["end_time"],
    ):
        raise HTTPException(status_code=409, detail="Worker already has an appointment at that time")

    return create_appointment(db, business_id, **data)


@router.get("", response_model=list[AppointmentRead])
def list_appointments_endpoint(
    business_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("appointments:read")),
):
    return list_appointments(db, business_id)


@router.get("/{appointment_id}", response_model=AppointmentRead)
def get_appointment_endpoint(
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("appointments:read")),
):
    appointment = get_appointment(db, business_id, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment_endpoint(
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("appointments:update")),
):
    appointment = get_appointment(db, business_id, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    data = payload.model_dump(exclude_unset=True)
    merged = {
        "customer_id": appointment.customer_id,
        "service_id": appointment.service_id,
        "worker_id": appointment.worker_id,
        "start_time": appointment.start_time,
        "end_time": appointment.end_time,
        "status": appointment.status,
    }
    merged.update(data)

    if merged["end_time"] <= merged["start_time"]:
        raise HTTPException(status_code=422, detail="end_time must be later than start_time")

    if not validate_references(
        db, business_id,
        merged["customer_id"], merged["service_id"], merged["worker_id"],
    ):
        raise HTTPException(status_code=400, detail="Invalid customer, service, or worker")

    if merged["status"] in ("scheduled", "confirmed") and has_worker_conflict(
        db, business_id, merged["worker_id"],
        merged["start_time"], merged["end_time"],
        exclude_appointment_id=appointment.id,
    ):
        raise HTTPException(status_code=409, detail="Worker already has an appointment at that time")

    return update_appointment(db, appointment, **data)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment_endpoint(
    business_id: uuid.UUID,
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("appointments:delete")),
):
    appointment = get_appointment(db, business_id, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    delete_appointment(db, appointment)
