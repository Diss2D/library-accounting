from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
