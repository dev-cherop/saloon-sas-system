import uuid
from datetime import date

from sqlalchemy import select,func
from sqlalchemy.orm import Session

from app.models.business import Branch, Business
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


def _business_is_active(db: Session, business_id: uuid.UUID) -> bool:
    return db.scalar(
        select(Business.id).where(
            Business.id == business_id,
            Business.is_active.is_(True),
        )
    ) is not None


def _valid_branch(
    db: Session,
    business_id: uuid.UUID,
    branch_id: uuid.UUID | None,
) -> bool:
    if branch_id is None:
        return True

    return db.scalar(
        select(Branch.id).where(
            Branch.id == branch_id,
            Branch.business_id == business_id,
            Branch.is_active.is_(True),
        )
    ) is not None


def create_expense(
    db: Session,
    business_id: uuid.UUID,
    payload: ExpenseCreate,
) -> Expense | None:
    if not _business_is_active(db, business_id):
        return None

    if not _valid_branch(db, business_id, payload.branch_id):
        raise ValueError(
            "Branch not found, inactive, or belongs to another business"
        )

    expense = Expense(business_id=business_id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(
    db: Session,
    business_id: uuid.UUID,
    *,
    branch_id: uuid.UUID | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[Expense]:
    stmt = select(Expense).where(Expense.business_id == business_id)

    if branch_id is not None:
        stmt = stmt.where(Expense.branch_id == branch_id)
    if category:
        stmt = stmt.where(Expense.category.ilike(f"%{category}%"))
    if start_date is not None:
        stmt = stmt.where(Expense.expense_date >= start_date)
    if end_date is not None:
        stmt = stmt.where(Expense.expense_date <= end_date)

    stmt = stmt.order_by(
        Expense.expense_date.desc(),
        Expense.created_at.desc(),
    )
    return list(db.scalars(stmt).all())


def get_expense(
    db: Session,
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
) -> Expense | None:
    return db.scalar(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.business_id == business_id,
        )
    )


def update_expense(
    db: Session,
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
    payload: ExpenseUpdate,
) -> Expense | None:
    expense = get_expense(db, business_id, expense_id)
    if expense is None:
        return None

    changes = payload.model_dump(exclude_unset=True)

    if "branch_id" in changes and not _valid_branch(
        db, business_id, changes["branch_id"]
    ):
        raise ValueError(
            "Branch not found, inactive, or belongs to another business"
        )

    for field, value in changes.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(
    db: Session,
    business_id: uuid.UUID,
    expense_id: uuid.UUID,
) -> bool:
    expense = get_expense(db, business_id, expense_id)
    if expense is None:
        return False

    db.delete(expense)
    db.commit()
    return True



def summarize_expenses(
    db: Session,
    business_id: uuid.UUID,
    *,
    branch_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    filters = [Expense.business_id == business_id]

    if branch_id is not None:
        filters.append(Expense.branch_id == branch_id)
    if start_date is not None:
        filters.append(Expense.expense_date >= start_date)
    if end_date is not None:
        filters.append(Expense.expense_date <= end_date)

    totals = db.execute(
        select(
            func.coalesce(func.sum(Expense.amount), 0),
            func.count(Expense.id),
        ).where(*filters)
    ).one()

    categories = db.execute(
        select(
            Expense.category,
            func.sum(Expense.amount),
            func.count(Expense.id),
        )
        .where(*filters)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    ).all()

    return {
        "total_amount": totals[0],
        "expense_count": totals[1],
        "categories": [
            {
                "category": row[0],
                "total_amount": row[1],
                "expense_count": row[2],
            }
            for row in categories
        ],
    }

