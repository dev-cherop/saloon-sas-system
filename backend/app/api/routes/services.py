import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from app.services.service import (
    create_service,
    delete_service,
    get_service,
    list_services,
    update_service,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service_endpoint(
    business_id: uuid.UUID,
    payload: ServiceCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("services:create")),
):
    service = create_service(
        db=db,
        business_id=business_id,
        name=payload.name,
        price=payload.price,
        duration_minutes=payload.duration_minutes,
        description=payload.description,
    )
    return service


@router.get("", response_model=list[ServiceRead])
def list_services_endpoint(
    business_id: uuid.UUID,
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("services:read")),
):
    return list_services(
        db,
        business_id,
        include_inactive=include_inactive,
    )


@router.get("/{service_id}", response_model=ServiceRead)
def get_service_endpoint(
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("services:read")),
):
    service = get_service(db, business_id, service_id)

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service


@router.patch("/{service_id}", response_model=ServiceRead)
def update_service_endpoint(
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("services:update")),
):
    service = update_service(
        db,
        business_id,
        service_id,
        **payload.model_dump(exclude_unset=True),
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return service


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_endpoint(
    business_id: uuid.UUID,
    service_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("services:delete")),
):
    deleted = delete_service(db, business_id, service_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found",
        )

    return None