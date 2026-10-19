import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.worker import WorkerCreate, WorkerRead, WorkerUpdate
from app.services.worker import (
    create_worker,
    delete_worker,
    get_worker,
    list_workers,
    update_worker,
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/workers",
    tags=["Workers"],
)


@router.post("", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
def create_worker_endpoint(
    business_id: uuid.UUID,
    payload: WorkerCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("workers:create")),
):
    return create_worker(
        db=db,
        business_id=business_id,
        **payload.model_dump(),
    )


@router.get("", response_model=list[WorkerRead])
def list_workers_endpoint(
    business_id: uuid.UUID,
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("workers:read")),
):
    return list_workers(db, business_id, include_inactive)


@router.get("/{worker_id}", response_model=WorkerRead)
def get_worker_endpoint(
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("workers:read")),
):
    worker = get_worker(db, business_id, worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.patch("/{worker_id}", response_model=WorkerRead)
def update_worker_endpoint(
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
    payload: WorkerUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("workers:update")),
):
    worker = update_worker(
        db,
        business_id,
        worker_id,
        **payload.model_dump(exclude_unset=True),
    )
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker_endpoint(
    business_id: uuid.UUID,
    worker_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("workers:delete")),
):
    if not delete_worker(db, business_id, worker_id):
        raise HTTPException(status_code=404, detail="Worker not found")
