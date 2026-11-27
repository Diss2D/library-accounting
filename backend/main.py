from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .auth import create_token, get_current_user, hash_password, unauthorized, verify_password
from .database import get_db
from .models import Reader, User
from .schemas import LoginData, RegisterData, SessionData, UserData

app = FastAPI(title="Библиотечный учет")


@app.post("/api/v1/users", response_model=UserData, status_code=201)
def register(data: RegisterData, response: Response, db: Annotated[Session, Depends(get_db)]):
    if db.scalar(select(User.id).where(User.email == data.email)) is not None:
        raise HTTPException(status_code=409, detail="Такая электронная почта уже зарегистрирована")

    try:
        reader = Reader(full_name=data.full_name, card_number=uuid4().hex)
        db.add(reader)
        db.flush()

        card_id = reader.id
        while db.scalar(select(Reader.id).where(Reader.card_number == f"ЧБ-{card_id:03d}")):
            card_id += 1
        reader.card_number = f"ЧБ-{card_id:03d}"

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            role="reader",
            reader_id=reader.id,
        )
        db.add(user)
        db.flush()
        result = UserData.model_validate(user)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if getattr(getattr(error.orig, "diag", None), "constraint_name", None) == "uq_users_email":
            raise HTTPException(
                status_code=409, detail="Такая электронная почта уже зарегистрирована"
            )
        raise HTTPException(status_code=409, detail="Конфликт при регистрации, повторите попытку")

    response.headers["Location"] = f"/api/v1/users/{result.id}"
    return result


@app.post("/api/v1/sessions", response_model=SessionData)
def login(data: LoginData, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise unauthorized("Неверная электронная почта или пароль")

    return SessionData(access_token=create_token(user.id), user=UserData.model_validate(user))


@app.get("/api/v1/users/{user_id}", response_model=UserData)
def get_user(user_id: int, user: Annotated[User, Depends(get_current_user)]):
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user
