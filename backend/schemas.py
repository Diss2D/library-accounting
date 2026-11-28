import re
from datetime import date
from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LoginData(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def check_email(cls, value):
        if not isinstance(value, str):
            raise ValueError("Введите электронную почту")

        try:
            email = validate_email(
                value.strip(), check_deliverability=False, test_environment=True
            ).normalized
        except EmailNotValidError as error:
            raise ValueError("Введите корректную электронную почту") from error

        return email.lower()


class RegisterData(LoginData):
    full_name: str = Field(min_length=1, max_length=150)

    @field_validator("full_name", mode="before")
    @classmethod
    def clean_name(cls, value):
        return value.strip() if isinstance(value, str) else value


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    reader_id: int | None


class SessionData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserData


class PublicationInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    publication_year: int = Field(gt=0, le=2147483647, strict=True)
    genre: str = Field(min_length=1, max_length=100)
    isbn: str | None = Field(default=None, max_length=17)

    @field_validator("isbn", mode="before")
    @classmethod
    def clean_isbn(cls, value):
        if isinstance(value, str):
            return value.strip() or None
        return value


class PublicationData(PublicationInput):
    id: int
    total_copies: int
    available_copies: int


class PublicationPage(BaseModel):
    items: list[PublicationData]
    total: int


class CopyInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    inventory_number: str = Field(min_length=1, max_length=50)


class CopyCreate(CopyInput):
    publication_id: int = Field(gt=0, le=2147483647, strict=True)


class CopyData(CopyCreate):
    id: int
    available: bool


class AvailableCopyData(CopyData):
    publication_title: str
    publication_author: str
    publication_year: int


class ReaderInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=1, max_length=150)
    card_number: str = Field(min_length=1, max_length=50)


class ReaderData(ReaderInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LoanCreate(BaseModel):
    reader_id: int = Field(gt=0, le=2147483647, strict=True)
    copy_id: int = Field(gt=0, le=2147483647, strict=True)
    loan_date: date
    due_date: date

    @field_validator("loan_date", "due_date", mode="before")
    @classmethod
    def check_date(cls, value):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Введите дату в формате ГГГГ-ММ-ДД")
        return value

    @model_validator(mode="after")
    def check_due_date(self):
        if self.due_date < self.loan_date:
            raise ValueError("Срок возврата не может быть раньше даты выдачи")
        return self


class LoanReturn(BaseModel):
    return_date: date

    @field_validator("return_date", mode="before")
    @classmethod
    def check_date(cls, value):
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Введите дату в формате ГГГГ-ММ-ДД")
        return value


class LoanData(BaseModel):
    id: int
    reader_id: int
    copy_id: int
    loan_date: date
    due_date: date
    return_date: date | None
    reader_name: str
    inventory_number: str
    publication_title: str
    status: str


class LoanPage(BaseModel):
    items: list[LoanData]
    total: int
