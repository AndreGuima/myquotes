from datetime import date

from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models.reading_list_book import ReadingListBook
from models.reading_list_log import ReadingListLog
from models.user import User
from schemas.reading_list import (
    ReadingListBookCreate,
    ReadingListBookRead,
    ReadingListBookUpdate,
    ReadingStatus,
)
from schemas.reading_log import ReadingLogCreate, ReadingLogRead
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reading-list", tags=["Reading List"])


@router.get("", response_model=list[ReadingListBookRead])
def list_books(
    status_filter: ReadingStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(ReadingListBook).filter(ReadingListBook.user_id == user.id)
    if status_filter:
        query = query.filter(ReadingListBook.status == status_filter.value)
    return query.order_by(ReadingListBook.id.desc()).all()


@router.post("", status_code=201, response_model=ReadingListBookRead)
def create_book(
    payload: ReadingListBookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = ReadingListBook(
        user_id=user.id,
        title=payload.title,
        author=payload.author,
        status=payload.status.value,
        rating=payload.rating,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=ReadingListBookRead)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = (
        db.query(ReadingListBook)
        .filter(ReadingListBook.id == book_id, ReadingListBook.user_id == user.id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book


@router.put("/{book_id}", response_model=ReadingListBookRead)
@router.patch("/{book_id}", response_model=ReadingListBookRead)
def update_book(
    book_id: int,
    payload: ReadingListBookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = (
        db.query(ReadingListBook)
        .filter(ReadingListBook.id == book_id, ReadingListBook.user_id == user.id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    if payload.rating is not None and payload.status is None:
        if book.status == ReadingStatus.to_read.value:
            raise HTTPException(
                status_code=400,
                detail="rating só é permitido para livros em leitura ou lidos",
            )

    if payload.title is not None:
        book.title = payload.title
    if payload.author is not None:
        book.author = payload.author

    if payload.status is not None:
        book.status = payload.status.value
        if payload.status == ReadingStatus.to_read:
            book.rating = None

    if payload.rating is not None:
        book.rating = payload.rating

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = (
        db.query(ReadingListBook)
        .filter(ReadingListBook.id == book_id, ReadingListBook.user_id == user.id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    db.delete(book)
    db.commit()
    return None


@router.get("/{book_id}/logs", response_model=list[ReadingLogRead])
def list_logs(
    book_id: int,
    limit: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = (
        db.query(ReadingListBook)
        .filter(ReadingListBook.id == book_id, ReadingListBook.user_id == user.id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    return (
        db.query(ReadingListLog)
        .filter(ReadingListLog.book_id == book.id)
        .order_by(ReadingListLog.log_date.desc())
        .limit(limit)
        .all()
    )


@router.post("/{book_id}/logs", response_model=ReadingLogRead)
def upsert_log(
    book_id: int,
    payload: ReadingLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = (
        db.query(ReadingListBook)
        .filter(ReadingListBook.id == book_id, ReadingListBook.user_id == user.id)
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    log_date = payload.log_date or date.today()
    log = (
        db.query(ReadingListLog)
        .filter(
            ReadingListLog.book_id == book.id,
            ReadingListLog.log_date == log_date,
        )
        .first()
    )
    if not log:
        log = ReadingListLog(
            book_id=book.id,
            log_date=log_date,
            comment=payload.comment,
        )
        db.add(log)
    else:
        log.comment = payload.comment

    db.commit()
    db.refresh(log)
    return log
