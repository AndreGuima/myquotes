from datetime import date, datetime, timedelta

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models.bank_account_transaction import BankAccountTransaction
from models.expense import Expense
from models.investment_income import InvestmentIncome
from models.user import User
from sqlalchemy import case, func
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/daily-cashflow")
def daily_cashflow(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Default to last 30 days
    if to_date is None:
        to_date = datetime.utcnow().date()
    if from_date is None:
        from_date = to_date - timedelta(days=29)

    if from_date > to_date:
        raise HTTPException(status_code=400, detail="'from' must be <= 'to'")

    # Group transactions by date (date portion of created_at)
    # Sum bank account transactions (exclude investment income transactions
    # because we will count them by InvestmentIncome.received_at to avoid
    # double-counting and to use the received date)
    rows = (
        db.query(
            func.date(BankAccountTransaction.created_at).label("date"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BankAccountTransaction.amount > 0,
                            BankAccountTransaction.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("incomings"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            BankAccountTransaction.amount < 0,
                            -BankAccountTransaction.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("outgoings"),
        )
        .filter(
            BankAccountTransaction.user_id == user.id,
            func.date(BankAccountTransaction.created_at) >= from_date,
            func.date(BankAccountTransaction.created_at) <= to_date,
            # Exclude transactions that represent investment incomes created
            # via the InvestmentIncome flow (these have description like
            # "Rendimento TICKER") and also exclude explicit income
            # adjustment/reversal types. Keep other transactions,
            # including manual positive adjustments that use the
            # INVESTMENT_INCOME enum but have a different description.
            ~(
                (BankAccountTransaction.transaction_type == "investment_income")
                & (BankAccountTransaction.description.ilike("Rendimento %"))
            ),
            BankAccountTransaction.transaction_type.notin_(
                [
                    "investment_income_adjustment",
                    "investment_income_reversal",
                ]
            ),
        )
        .group_by(func.date(BankAccountTransaction.created_at))
        .order_by(func.date(BankAccountTransaction.created_at).desc())
        .all()
    )
    # Also sum credit expenses by launch_date (these are not in account
    # transactions yet)
    expense_rows = (
        db.query(
            Expense.launch_date.label("date"),
            func.coalesce(func.sum(Expense.value), 0).label("credit_outgoings"),
        )
        .filter(
            Expense.user_id == user.id,
            Expense.payment_method == "credit",
            Expense.launch_date >= from_date,
            Expense.launch_date <= to_date,
        )
        .group_by(Expense.launch_date)
        .order_by(Expense.launch_date.desc())
        .all()
    )

    data = {}
    for row in rows:
        key = row.date.isoformat()
        data[key] = {
            "date": key,
            "incomings": float(row.incomings),
            "outgoings": float(row.outgoings),
        }

    for er in expense_rows:
        key = er.date.isoformat()
        if key in data:
            data[key]["outgoings"] = data[key]["outgoings"] + float(er.credit_outgoings)
        else:
            data[key] = {
                "date": key,
                "incomings": 0.0,
                "outgoings": float(er.credit_outgoings),
            }

    # Include investment incomes by their received_at date (count as incomings
    # regardless of income_type)
    income_rows = (
        db.query(
            InvestmentIncome.received_at.label("date"),
            func.coalesce(func.sum(InvestmentIncome.amount), 0).label("total"),
        )
        .filter(
            InvestmentIncome.user_id == user.id,
            InvestmentIncome.received_at >= from_date,
            InvestmentIncome.received_at <= to_date,
        )
        .group_by(InvestmentIncome.received_at)
        .order_by(InvestmentIncome.received_at.desc())
        .all()
    )

    for ir in income_rows:
        key = ir.date.isoformat()
        if key in data:
            data[key]["incomings"] = data[key]["incomings"] + float(ir.total)
        else:
            data[key] = {"date": key, "incomings": float(ir.total), "outgoings": 0.0}

    # Return ordered list, most recent first
    result = sorted(data.values(), key=lambda r: r["date"], reverse=True)
    return result
