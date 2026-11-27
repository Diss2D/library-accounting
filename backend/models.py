from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Publication(Base):
    __tablename__ = "publications"
    __table_args__ = (
        CheckConstraint("publication_year > 0", name="ck_publications_year"),
        UniqueConstraint("isbn", name="uq_publications_isbn"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    author: Mapped[str] = mapped_column(String(255))
    publication_year: Mapped[int]
    genre: Mapped[str] = mapped_column(String(100))
    isbn: Mapped[str | None] = mapped_column(String(17))

    copies: Mapped[list["Copy"]] = relationship(back_populates="publication", passive_deletes="all")


class Copy(Base):
    __tablename__ = "copies"
    __table_args__ = (UniqueConstraint("inventory_number", name="uq_copies_inventory_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_id: Mapped[int] = mapped_column(ForeignKey("publications.id"))
    inventory_number: Mapped[str] = mapped_column(String(50))

    publication: Mapped["Publication"] = relationship(back_populates="copies")
    loans: Mapped[list["Loan"]] = relationship(back_populates="copy")


class Reader(Base):
    __tablename__ = "readers"
    __table_args__ = (UniqueConstraint("card_number", name="uq_readers_card_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    card_number: Mapped[str] = mapped_column(String(50))

    loans: Mapped[list["Loan"]] = relationship(back_populates="reader")
    user: Mapped["User"] = relationship(back_populates="reader")


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        CheckConstraint("due_date >= loan_date", name="ck_loans_due_date"),
        CheckConstraint("return_date >= loan_date", name="ck_loans_return_date"),
        Index(
            "uq_loans_open_copy",
            "copy_id",
            unique=True,
            postgresql_where=text("return_date IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    copy_id: Mapped[int] = mapped_column(ForeignKey("copies.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"))
    loan_date: Mapped[date] = mapped_column(Date)
    due_date: Mapped[date] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date)

    copy: Mapped["Copy"] = relationship(back_populates="loans")
    reader: Mapped["Reader"] = relationship(back_populates="loans")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("reader_id", name="uq_users_reader_id"),
        CheckConstraint("role IN ('librarian', 'reader')", name="ck_users_role"),
        CheckConstraint(
            "(role = 'librarian' AND reader_id IS NULL) OR "
            "(role = 'reader' AND reader_id IS NOT NULL)",
            name="ck_users_reader_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    reader_id: Mapped[int | None] = mapped_column(ForeignKey("readers.id"))

    reader: Mapped["Reader | None"] = relationship(back_populates="user")
