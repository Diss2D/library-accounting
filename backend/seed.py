import json
import os
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import select

from .auth import hash_password
from .database import SessionLocal
from .models import Copy, Loan, Publication, Reader, User


def seed():
    data_path = Path(__file__).parent / "data" / "publications.json"
    publications_data = json.loads(data_path.read_text(encoding="utf-8"))
    password = os.environ["DEMO_PASSWORD"]
    if not password:
        raise ValueError("Укажите DEMO_PASSWORD")

    with SessionLocal.begin() as db:
        for model in (Publication, Copy, Reader, User, Loan):
            if db.scalar(select(model.id).limit(1)) is not None:
                print("База уже содержит данные. Начальное наполнение пропущено.")
                return

        publications = [Publication(**item) for item in publications_data]
        db.add_all(publications)
        db.flush()

        publication_numbers = [1, 1, 2, 3, 4, 6, 7, 11]
        publication_numbers += [i for i in range(1, 31) if i not in publication_numbers]
        publication_numbers += [1, 2, 6, 11, 16]
        copies = [
            Copy(publication_id=publications[number - 1].id, inventory_number=f"ИНВ-{i:03d}")
            for i, number in enumerate(publication_numbers, start=1)
        ]
        db.add_all(copies)

        readers = [
            Reader(full_name="Иванов Иван Иванович", card_number="ЧБ-001"),
            Reader(full_name="Александрова Александра Александровна", card_number="ЧБ-002"),
            Reader(full_name="Максимов Максим Максимович", card_number="ЧБ-003"),
        ]
        db.add_all(readers)
        db.flush()

        users = [
            User(
                email="librarian@example.test",
                role="librarian",
                password_hash=hash_password(password),
            )
        ]
        for name, reader in zip(("ivanov", "alexandrova", "maksimov"), readers):
            users.append(
                User(
                    email=f"{name}@example.test",
                    role="reader",
                    reader_id=reader.id,
                    password_hash=hash_password(password),
                )
            )
        db.add_all(users)

        today = date.today()
        loan_data = [
            (1, 1, 5, None),
            (3, 1, 27, None),
            (4, 2, 23, 12),
            (6, 2, 3, None),
        ]
        monthly_copies = [
            (1, 3, 4, 6, 8),
            (1, 3, 6),
            (1, 3, 4, 6, 8, 10, 17),
            (1, 6, 8, 12),
            (1, 3, 4, 6, 9, 22),
            (1, 3, 6, 8, 18),
        ]
        for month, numbers in enumerate(monthly_copies, start=1):
            for i, copy_number in enumerate(numbers):
                loan_data.append((copy_number, (month + i) % 3 + 1, month * 30 + 15 + i, 7 + i))

        loans = []
        for copy_number, reader_number, days_ago, returned_after in loan_data:
            loan_date = today - timedelta(days=days_ago)
            loans.append(
                Loan(
                    copy_id=copies[copy_number - 1].id,
                    reader_id=readers[reader_number - 1].id,
                    loan_date=loan_date,
                    due_date=loan_date + timedelta(days=14),
                    return_date=(
                        loan_date + timedelta(days=returned_after)
                        if returned_after is not None
                        else None
                    ),
                )
            )
        db.add_all(loans)

    print(
        f"Добавлено: {len(publications)} изданий, {len(copies)} экземпляров, "
        f"{len(readers)} читателя, {len(users)} учетные записи, {len(loans)} выдачи."
    )


if __name__ == "__main__":
    seed()
