import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.authorization import require_permission
from app.db import get_db
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services.expense import (
    create_expense,
    delete_expense,
    get_expense,
    list_expenses,
    update_expense,
    summarize_expenses,
    
)

router = APIRouter(
    prefix="/api/v1/businesses/{business_id}/expenses",
    tags=["Expenses"],
)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(
    business_id: uuid.UUID,
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:create")),
):
    try:
        expense = create_expense(db, business_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if expense is None:
        raise HTTPException(status_code=404, detail="Business not found or inactive")
    return expense


@router.get("", response_model=list[ExpenseRead])
def list_expenses_endpoint(
    business_id: uuid.UUID,
    branch_id: uuid.UUID | None = None,
    category: str | None = Query(default=None, max_length=100),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:read")),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")

    return list_expenses(
        db,
        business_id,
        branch_id=branch_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )



@router.get("/summary")
def expense_summary_endpoint(
    business_id: uuid.UUID,
    branch_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:read")),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date",
        )

    return summarize_expenses(
        db,
        business_id,
        branch_id=branch_id,
        start_date=start_date,
        end_date=end_date,
    )



@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense_endpoint(
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:read")),
):
    expense = get_expense(db, business_id, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense_endpoint(
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:update")),
):
    try:
        expense = update_expense(db, business_id, expense_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_endpoint(
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    _membership=Depends(require_permission("expenses:delete")),
):
    if not delete_expense(db, business_id, expense_id):
        raise HTTPException(status_code=404, detail="Expense not found")
