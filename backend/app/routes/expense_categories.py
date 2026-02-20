from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.expense import Expense
from models.expense_category import ExpenseCategory
from models.user import User
from schemas.expense_category import (
    ExpenseCategoryCreate,
    ExpenseCategoryRead,
    ExpenseCategoryUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(prefix="/expense-categories", tags=["Expense Categories"])


def _to_response(category: ExpenseCategory) -> ExpenseCategoryRead:
    return ExpenseCategoryRead(
        id=category.id,
        name=category.name,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def _get_user_category_or_404(
    db: Session,
    user_id: int,
    category_id: int,
) -> ExpenseCategory:
    category = (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.id == category_id, ExpenseCategory.user_id == user_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category


@router.get("", response_model=list[ExpenseCategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    categories = (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.user_id == user.id)
        .order_by(ExpenseCategory.name.asc(), ExpenseCategory.id.asc())
        .all()
    )
    return [_to_response(category) for category in categories]


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=ExpenseCategoryRead
)
def create_category(
    payload: ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    clean_name = payload.name.strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nome é obrigatório")

    exists = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.user_id == user.id,
            ExpenseCategory.name == clean_name,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Categoria já existe")

    category = ExpenseCategory(user_id=user.id, name=clean_name)
    db.add(category)
    db.commit()

    created = _get_user_category_or_404(db, user.id, category.id)
    return _to_response(created)


@router.patch("/{category_id}", response_model=ExpenseCategoryRead)
def update_category(
    category_id: int,
    payload: ExpenseCategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    category = _get_user_category_or_404(db, user.id, category_id)

    if payload.name is not None:
        clean_name = payload.name.strip()
        if not clean_name:
            raise HTTPException(status_code=400, detail="Nome é obrigatório")

        exists = (
            db.query(ExpenseCategory)
            .filter(
                ExpenseCategory.user_id == user.id,
                ExpenseCategory.name == clean_name,
                ExpenseCategory.id != category_id,
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=400, detail="Categoria já existe")

        category.name = clean_name

    db.commit()

    updated = _get_user_category_or_404(db, user.id, category_id)
    return _to_response(updated)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    category = _get_user_category_or_404(db, user.id, category_id)
    has_expenses = (
        db.query(Expense.id)
        .filter(Expense.user_id == user.id, Expense.expense_category_id == category_id)
        .first()
    )
    if has_expenses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Categoria em uso por despesas. "
                "Atualize as despesas antes de remover."
            ),
        )
    db.delete(category)
    db.commit()
    return None
