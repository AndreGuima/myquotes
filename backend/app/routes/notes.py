from core.dependencies import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.note import Note
from models.user import User
from schemas.note import NoteCreate, NoteRead, NoteUpdate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/notes", tags=["Notes"])


def _to_response(note: Note) -> NoteRead:
    return NoteRead(
        id=note.id,
        title=note.title,
        content=note.content,
        createdAt=note.created_at,
        updatedAt=note.updated_at,
    )


def _get_user_note_or_404(db: Session, user_id: int, note_id: int) -> Note:
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Anotação não encontrada")
    return note


@router.get("", response_model=list[NoteRead])
def list_notes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .filter(Note.user_id == user.id)
        .order_by(Note.updated_at.desc(), Note.id.desc())
        .all()
    )
    return [_to_response(note) for note in notes]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=NoteRead)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    title = payload.title.strip()
    content = payload.content.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Título da anotação é obrigatório")
    if not content:
        raise HTTPException(
            status_code=400, detail="Conteúdo da anotação é obrigatório"
        )

    note = Note(user_id=user.id, title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return _to_response(note)


@router.get("/{note_id}", response_model=NoteRead)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _to_response(_get_user_note_or_404(db, user.id, note_id))


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = _get_user_note_or_404(db, user.id, note_id)

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(
                status_code=400, detail="Título da anotação é obrigatório"
            )
        note.title = title

    if payload.content is not None:
        content = payload.content.strip()
        if not content:
            raise HTTPException(
                status_code=400, detail="Conteúdo da anotação é obrigatório"
            )
        note.content = content

    db.commit()
    db.refresh(note)
    return _to_response(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    note = _get_user_note_or_404(db, user.id, note_id)
    db.delete(note)
    db.commit()
    return None
