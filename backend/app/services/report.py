import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.expense import Expense
from app.models.payment import Payment


APPOINTMENT_STATUSES = (
    "scheduled",
    "confirmed",
    "completed",
    "cancelled",
    "no_show",
)


def get_business_report(
    db: Session,
    business_id: uuid.UUID,
    start_date: date,
    end_date: date,
) -> dict:
    revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.business_id == business_id,
            func.date(Payment.paid_at) >= start_date,
            func.date(Payment.paid_at) <= end_date,
        )
    )

    expenses = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.business_id == business_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        )
    )

    appointment_count = db.scalar(
        select(func.count(Appointment.id)).where(
            Appointment.business_id == business_id,
            func.date(Appointment.start_time) >= start_date,
            func.date(Appointment.start_time) <= end_date,
        )
    )

    payment_rows = db.execute(
        select(Payment.payment_method, func.sum(Payment.amount))
        .where(
            Payment.business_id == business_id,
            func.date(Payment.paid_at) >= start_date,
            func.date(Payment.paid_at) <= end_date,
        )
        .group_by(Payment.payment_method)
    ).all()

    status_rows = db.execute(
        select(Appointment.status, func.count(Appointment.id))
        .where(
            Appointment.business_id == business_id,
            func.date(Appointment.start_time) >= start_date,
            func.date(Appointment.start_time) <= end_date,
        )
        .group_by(Appointment.status)
    ).all()

    daily_revenue_rows = db.execute(
        select(func.date(Payment.paid_at), func.sum(Payment.amount))
        .where(
            Payment.business_id == business_id,
            func.date(Payment.paid_at) >= start_date,
            func.date(Payment.paid_at) <= end_date,
        )
        .group_by(func.date(Payment.paid_at))
    ).all()

    daily_expense_rows = db.execute(
        select(Expense.expense_date, func.sum(Expense.amount))
        .where(
            Expense.business_id == business_id,
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
        )
        .group_by(Expense.expense_date)
    ).all()

    daily_totals = {}

    for day, amount in daily_revenue_rows:
        key = str(day)
        daily_totals.setdefault(
            key, {"date": key, "revenue": 0, "expenses": 0}
        )
        daily_totals[key]["revenue"] = amount

    for day, amount in daily_expense_rows:
        key = str(day)
        daily_totals.setdefault(
            key, {"date": key, "revenue": 0, "expenses": 0}
        )
        daily_totals[key]["expenses"] = amount

    appointment_statuses = {
        status: 0 for status in APPOINTMENT_STATUSES
    }
    appointment_statuses.update(
        {status: count for status, count in status_rows}
    )

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": revenue,
        "total_expenses": expenses,
        "net_profit": revenue - expenses,
        "appointment_count": appointment_count,
        "revenue_by_payment_method": [
            {"method": method, "total": total}
            for method, total in payment_rows
        ],
        "appointments_by_status": appointment_statuses,
        "daily_totals": sorted(
            daily_totals.values(), key=lambda item: item["date"]
        ),
    }
