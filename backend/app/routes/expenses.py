from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.bank_account import BankAccount
from models.credit_card import CreditCard
from models.expense import Expense
from models.expense_category import ExpenseCategory
from models.user import User
from schemas.expense import (
    ExpenseCreate,
    ExpenseRead,
    ExpenseSummaryCategoryRead,
    ExpenseSummaryRead,
    ExpenseUpdate,
)
from sqlalchemy import case, func
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _to_response(expense: Expense) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
        value=expense.value,
        description=expense.description,
        expense_category_id=expense.expense_category_id,
        expense_category_name=expense.expense_category.name,
        payment_method=expense.payment_method,
        bank_account_id=expense.bank_account_id,
        bank_account_name=expense.bank_account.name if expense.bank_account else None,
        credit_card_id=expense.credit_card_id,
        credit_card_name=expense.credit_card.name if expense.credit_card else None,
        launch_date=expense.launch_date,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
    )


def _to_money_decimal(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_user_expense_or_404(db: Session, user_id: int, expense_id: int) -> Expense:
    expense = (
        db.query(Expense)
        .options(
            joinedload(Expense.bank_account),
            joinedload(Expense.credit_card),
            joinedload(Expense.expense_category),
        )
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return expense


def _validate_account_belongs_to_user(
    db: Session, user_id: int, account_id: int
) -> None:
    account = (
        db.query(BankAccount)
        .filter(BankAccount.id == account_id, BankAccount.user_id == user_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=400, detail="Conta bancária inválida")


def _validate_card_belongs_to_user(db: Session, user_id: int, card_id: int) -> None:
    card = (
        db.query(CreditCard)
        .filter(CreditCard.id == card_id, CreditCard.user_id == user_id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=400, detail="Cartão inválido")


def _validate_category_belongs_to_user(
    db: Session,
    user_id: int,
    category_id: int,
) -> None:
    category = (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.id == category_id, ExpenseCategory.user_id == user_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=400, detail="Categoria inválida")


def _apply_expense_filters(
    *,
    query: SAQuery,
    db: Session,
    user_id: int,
    year: int | None,
    month: int | None,
    from_date: date | None,
    to_date: date | None,
    category_id: int | None,
) -> SAQuery:
    if month is not None and year is None:
        raise HTTPException(
            status_code=400, detail="year is required when month is provided"
        )

    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=400, detail="'from' must be less than or equal to 'to'"
        )

    if category_id is not None:
        _validate_category_belongs_to_user(db, user_id, category_id)

    query = query.filter(Expense.user_id == user_id)

    if year is not None and month is None:
        query = query.filter(Expense.launch_date >= date(year, 1, 1))
        query = query.filter(Expense.launch_date <= date(year, 12, 31))

    if year is not None and month is not None:
        period_start = date(year, month, 1)
        if month == 12:
            period_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(year, month + 1, 1) - timedelta(days=1)
        query = query.filter(Expense.launch_date >= period_start)
        query = query.filter(Expense.launch_date <= period_end)

    if from_date is not None:
        query = query.filter(Expense.launch_date >= from_date)

    if to_date is not None:
        query = query.filter(Expense.launch_date <= to_date)

    if category_id is not None:
        query = query.filter(Expense.expense_category_id == category_id)

    return query


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    year: int | None = Query(default=None, ge=1900, le=9999),
    month: int | None = Query(default=None, ge=1, le=12),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    category_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Expense).options(
        joinedload(Expense.bank_account),
        joinedload(Expense.credit_card),
        joinedload(Expense.expense_category),
    )
    query = _apply_expense_filters(
        query=query,
        db=db,
        user_id=user.id,
        year=year,
        month=month,
        from_date=from_date,
        to_date=to_date,
        category_id=category_id,
    )
    expenses = (
        query.order_by(Expense.launch_date.desc(), Expense.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [_to_response(expense) for expense in expenses]


@router.get("/summary", response_model=ExpenseSummaryRead)
def get_expenses_summary(
    year: int | None = Query(default=None, ge=1900, le=9999),
    month: int | None = Query(default=None, ge=1, le=12),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    category_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base_query = _apply_expense_filters(
        query=db.query(Expense),
        db=db,
        user_id=user.id,
        year=year,
        month=month,
        from_date=from_date,
        to_date=to_date,
        category_id=category_id,
    )

    summary_row = base_query.with_entities(
        func.coalesce(func.sum(Expense.value), 0),
        func.coalesce(func.avg(Expense.value), 0),
        func.count(Expense.id),
        func.coalesce(
            func.sum(
                case((Expense.payment_method == "credit", Expense.value), else_=0)
            ),
            0,
        ),
        func.coalesce(
            func.sum(case((Expense.payment_method == "debit", Expense.value), else_=0)),
            0,
        ),
    ).one()

    by_category_rows = (
        base_query.join(
            ExpenseCategory, ExpenseCategory.id == Expense.expense_category_id
        )
        .with_entities(
            Expense.expense_category_id,
            ExpenseCategory.name,
            func.coalesce(func.sum(Expense.value), 0),
            func.count(Expense.id),
        )
        .group_by(Expense.expense_category_id, ExpenseCategory.name)
        .order_by(func.sum(Expense.value).desc(), func.count(Expense.id).desc())
        .all()
    )

    by_category = [
        ExpenseSummaryCategoryRead(
            category_id=row[0],
            category_name=row[1],
            total=_to_money_decimal(row[2]),
            count=row[3],
        )
        for row in by_category_rows
    ]

    return ExpenseSummaryRead(
        total=_to_money_decimal(summary_row[0]),
        average=_to_money_decimal(summary_row[1]),
        count=summary_row[2],
        credit_total=_to_money_decimal(summary_row[3]),
        debit_total=_to_money_decimal(summary_row[4]),
        by_category=by_category,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ExpenseRead)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _validate_category_belongs_to_user(db, user.id, payload.expense_category_id)

    if payload.payment_method == "debit":
        _validate_account_belongs_to_user(db, user.id, payload.bank_account_id)

    if payload.payment_method == "credit":
        _validate_card_belongs_to_user(db, user.id, payload.credit_card_id)

    expense = Expense(
        user_id=user.id,
        value=payload.value,
        description=payload.description.strip(),
        expense_category_id=payload.expense_category_id,
        payment_method=payload.payment_method,
        bank_account_id=payload.bank_account_id,
        credit_card_id=payload.credit_card_id,
        launch_date=payload.launch_date,
    )

    if not expense.description:
        raise HTTPException(status_code=400, detail="Descrição é obrigatória")

    db.add(expense)
    db.commit()
    db.expire_all()

    created = _get_user_expense_or_404(db, user.id, expense.id)
    return _to_response(created)


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = _get_user_expense_or_404(db, user.id, expense_id)

    next_payment_method = payload.payment_method or expense.payment_method
    next_expense_category_id = (
        payload.expense_category_id
        if payload.expense_category_id is not None
        else expense.expense_category_id
    )
    next_bank_account_id = (
        payload.bank_account_id
        if payload.bank_account_id is not None
        else expense.bank_account_id
    )
    next_credit_card_id = (
        payload.credit_card_id
        if payload.credit_card_id is not None
        else expense.credit_card_id
    )

    if next_payment_method == "debit":
        if next_bank_account_id is None:
            raise HTTPException(
                status_code=400, detail="bank_account_id é obrigatório para débito"
            )
        next_credit_card_id = None
        _validate_account_belongs_to_user(db, user.id, next_bank_account_id)

    if next_payment_method == "credit":
        if next_credit_card_id is None:
            raise HTTPException(
                status_code=400, detail="credit_card_id é obrigatório para crédito"
            )
        next_bank_account_id = None
        _validate_card_belongs_to_user(db, user.id, next_credit_card_id)

    _validate_category_belongs_to_user(db, user.id, next_expense_category_id)

    if payload.value is not None:
        expense.value = payload.value
    if payload.description is not None:
        clean_description = payload.description.strip()
        if not clean_description:
            raise HTTPException(status_code=400, detail="Descrição é obrigatória")
        expense.description = clean_description
    if payload.launch_date is not None:
        expense.launch_date = payload.launch_date

    expense.expense_category_id = next_expense_category_id
    expense.payment_method = next_payment_method
    expense.bank_account_id = next_bank_account_id
    expense.credit_card_id = next_credit_card_id

    db.commit()
    db.expire_all()

    updated = _get_user_expense_or_404(db, user.id, expense_id)
    return _to_response(updated)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = _get_user_expense_or_404(db, user.id, expense_id)
    db.delete(expense)
    db.commit()
    return None
