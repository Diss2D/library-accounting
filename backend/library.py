from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .auth import get_current_user, require_librarian, require_reader
from .database import get_db
from .models import Copy, Loan, Publication, Reader, User
from .schemas import (
    AvailableCopyData,
    CopyCreate,
    CopyData,
    CopyInput,
    LoanCreate,
    LoanData,
    LoanReturn,
    PublicationData,
    PublicationInput,
    PublicationPage,
    ReaderData,
    ReaderInput,
)

router = APIRouter(prefix="/api/v1")

Database = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
Librarian = Annotated[User, Depends(require_librarian)]
CurrentReader = Annotated[User, Depends(require_reader)]


def save_changes(db: Session):
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        constraint = getattr(getattr(error.orig, "diag", None), "constraint_name", None)
        messages = {
            "uq_publications_isbn": ("Издание с таким ISBN уже существует", "isbn"),
            "uq_copies_inventory_number": (
                "Такой инвентарный номер уже существует",
                "inventory_number",
            ),
            "uq_readers_card_number": (
                "Такой номер читательского билета уже существует",
                "card_number",
            ),
            "uq_loans_open_copy": ("Экземпляр уже выдан", "copy_id"),
            "copies_publication_id_fkey": (
                "Издание связано с экземплярами или не существует",
                None,
            ),
        }
        message, field = messages.get(constraint, ("Конфликт данных", None))
        raise HTTPException(status_code=409, detail={"message": message, "field": field}) from error


def available_condition():
    return ~Copy.loans.any(Loan.return_date.is_(None))


def publication_query():
    total = (
        select(func.count(Copy.id))
        .where(Copy.publication_id == Publication.id)
        .correlate(Publication)
        .scalar_subquery()
    )
    available = (
        select(func.count(Copy.id))
        .where(Copy.publication_id == Publication.id, available_condition())
        .correlate(Publication)
        .scalar_subquery()
    )
    return select(Publication, total, available)


def publication_data(publication: Publication, total: int, available: int):
    return PublicationData(
        id=publication.id,
        title=publication.title,
        author=publication.author,
        publication_year=publication.publication_year,
        genre=publication.genre,
        isbn=publication.isbn,
        total_copies=total,
        available_copies=available,
    )


def find_publication(db: Session, publication_id: int):
    publication = db.get(Publication, publication_id)
    if publication is None:
        raise HTTPException(status_code=404, detail="Издание не найдено")
    return publication


def get_publication_data(db: Session, publication_id: int):
    row = db.execute(publication_query().where(Publication.id == publication_id)).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Издание не найдено")
    return publication_data(*row)


@router.get("/publications/genres", response_model=list[str])
def get_genres(db: Database, user: CurrentUser):
    return db.scalars(select(Publication.genre).distinct().order_by(Publication.genre)).all()


@router.get("/publications", response_model=PublicationPage)
def get_publications(
    db: Database,
    user: CurrentUser,
    search: str = Query(default="", max_length=255),
    genre: str = Query(default="", max_length=100),
    sort: Literal["title", "author", "publication_year"] = "title",
    direction: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1, le=2147483647),
    page_size: int = Query(default=5, ge=1, le=100),
):
    conditions = []
    if search.strip():
        conditions.append(
            or_(
                Publication.title.icontains(search.strip(), autoescape=True),
                Publication.author.icontains(search.strip(), autoescape=True),
            )
        )
    if genre:
        conditions.append(Publication.genre == genre)

    total = db.scalar(select(func.count(Publication.id)).where(*conditions)) or 0
    column = {
        "title": Publication.title,
        "author": Publication.author,
        "publication_year": Publication.publication_year,
    }[sort]
    order = column.desc() if direction == "desc" else column.asc()
    rows = db.execute(
        publication_query()
        .where(*conditions)
        .order_by(order, Publication.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return PublicationPage(items=[publication_data(*row) for row in rows], total=total)


@router.get("/publications/{publication_id}", response_model=PublicationData)
def get_publication(publication_id: int, db: Database, user: CurrentUser):
    return get_publication_data(db, publication_id)


@router.post("/publications", response_model=PublicationData, status_code=201)
def create_publication(data: PublicationInput, response: Response, db: Database, user: Librarian):
    publication = Publication(**data.model_dump())
    db.add(publication)
    save_changes(db)
    response.headers["Location"] = f"/api/v1/publications/{publication.id}"
    return get_publication_data(db, publication.id)


@router.put("/publications/{publication_id}", response_model=PublicationData)
def update_publication(publication_id: int, data: PublicationInput, db: Database, user: Librarian):
    publication = find_publication(db, publication_id)
    for field, value in data.model_dump().items():
        setattr(publication, field, value)
    save_changes(db)
    return get_publication_data(db, publication_id)


@router.delete("/publications/{publication_id}", status_code=204)
def delete_publication(publication_id: int, db: Database, user: Librarian):
    publication = find_publication(db, publication_id)
    if db.scalar(select(Copy.id).where(Copy.publication_id == publication_id).limit(1)) is not None:
        raise HTTPException(status_code=409, detail="Нельзя удалить издание, имеющее экземпляры")
    db.delete(publication)
    save_changes(db)
    return Response(status_code=204)


def copy_data(copy: Copy, available: bool):
    return CopyData(
        id=copy.id,
        publication_id=copy.publication_id,
        inventory_number=copy.inventory_number,
        available=available,
    )


def get_copy_data(db: Session, copy_id: int):
    row = db.execute(select(Copy, available_condition()).where(Copy.id == copy_id)).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Экземпляр не найден")
    return copy_data(*row)


@router.get("/publications/{publication_id}/copies", response_model=list[CopyData])
def get_copies(publication_id: int, db: Database, user: Librarian):
    find_publication(db, publication_id)
    rows = db.execute(
        select(Copy, available_condition())
        .where(Copy.publication_id == publication_id)
        .order_by(Copy.id)
    ).all()
    return [copy_data(*row) for row in rows]


@router.get("/copies/available", response_model=list[AvailableCopyData])
def get_available_copies(db: Database, user: Librarian):
    copies = db.scalars(
        select(Copy)
        .where(available_condition())
        .options(joinedload(Copy.publication))
        .order_by(Copy.id)
    ).all()
    return [
        AvailableCopyData(
            **copy_data(copy, True).model_dump(),
            publication_title=copy.publication.title,
            publication_author=copy.publication.author,
            publication_year=copy.publication.publication_year,
        )
        for copy in copies
    ]


@router.get("/copies/{copy_id}", response_model=CopyData)
def get_copy(copy_id: int, db: Database, user: Librarian):
    return get_copy_data(db, copy_id)


@router.post("/copies", response_model=CopyData, status_code=201)
def create_copy(data: CopyCreate, response: Response, db: Database, user: Librarian):
    find_publication(db, data.publication_id)
    copy = Copy(**data.model_dump())
    db.add(copy)
    save_changes(db)
    response.headers["Location"] = f"/api/v1/copies/{copy.id}"
    return get_copy_data(db, copy.id)


@router.put("/copies/{copy_id}", response_model=CopyData)
def update_copy(copy_id: int, data: CopyInput, db: Database, user: Librarian):
    copy = db.get(Copy, copy_id)
    if copy is None:
        raise HTTPException(status_code=404, detail="Экземпляр не найден")
    copy.inventory_number = data.inventory_number
    save_changes(db)
    return get_copy_data(db, copy_id)


@router.get("/readers", response_model=list[ReaderData])
def get_readers(db: Database, user: Librarian):
    return db.scalars(select(Reader).order_by(Reader.id)).all()


@router.put("/readers/{reader_id}", response_model=ReaderData)
def update_reader(reader_id: int, data: ReaderInput, db: Database, user: Librarian):
    reader = db.get(Reader, reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    reader.full_name = data.full_name
    reader.card_number = data.card_number
    save_changes(db)
    return reader


def loan_data(loan: Loan):
    if loan.return_date is not None:
        status = "completed"
    elif loan.due_date < date.today():
        status = "overdue"
    else:
        status = "active"
    return LoanData(
        id=loan.id,
        reader_id=loan.reader_id,
        copy_id=loan.copy_id,
        loan_date=loan.loan_date,
        due_date=loan.due_date,
        return_date=loan.return_date,
        reader_name=loan.reader.full_name,
        inventory_number=loan.copy.inventory_number,
        publication_title=loan.copy.publication.title,
        status=status,
    )


def loan_query():
    return select(Loan).options(
        joinedload(Loan.reader), joinedload(Loan.copy).joinedload(Copy.publication)
    )


@router.get("/loans", response_model=list[LoanData])
def get_loans(db: Database, user: Librarian):
    loans = db.scalars(loan_query().order_by(Loan.id)).all()
    return [loan_data(loan) for loan in loans]


@router.get("/loans/mine", response_model=list[LoanData])
def get_my_loans(db: Database, user: CurrentReader):
    loans = db.scalars(loan_query().where(Loan.reader_id == user.reader_id).order_by(Loan.id)).all()
    return [loan_data(loan) for loan in loans]


@router.get("/loans/{loan_id}", response_model=LoanData)
def get_loan(loan_id: int, db: Database, user: Librarian):
    loan = db.scalar(loan_query().where(Loan.id == loan_id))
    if loan is None:
        raise HTTPException(status_code=404, detail="Выдача не найдена")
    return loan_data(loan)


@router.post("/loans", response_model=LoanData, status_code=201)
def create_loan(data: LoanCreate, response: Response, db: Database, user: Librarian):
    if db.get(Reader, data.reader_id) is None:
        raise HTTPException(status_code=404, detail="Читатель не найден")
    if db.get(Copy, data.copy_id) is None:
        raise HTTPException(status_code=404, detail="Экземпляр не найден")
    if (
        db.scalar(select(Loan.id).where(Loan.copy_id == data.copy_id, Loan.return_date.is_(None)))
        is not None
    ):
        raise HTTPException(status_code=409, detail="Экземпляр уже выдан")
    loan = Loan(**data.model_dump())
    db.add(loan)
    save_changes(db)
    response.headers["Location"] = f"/api/v1/loans/{loan.id}"
    return loan_data(loan)


@router.patch("/loans/{loan_id}", response_model=LoanData)
def return_loan(loan_id: int, data: LoanReturn, db: Database, user: Librarian):
    loan = db.scalar(select(Loan).where(Loan.id == loan_id).with_for_update())
    if loan is None:
        raise HTTPException(status_code=404, detail="Выдача не найдена")
    if loan.return_date is not None:
        raise HTTPException(status_code=409, detail="Экземпляр уже возвращен")
    if data.return_date < loan.loan_date:
        raise HTTPException(
            status_code=422, detail="Дата возврата не может быть раньше даты выдачи"
        )
    loan.return_date = data.return_date
    save_changes(db)
    return loan_data(loan)
