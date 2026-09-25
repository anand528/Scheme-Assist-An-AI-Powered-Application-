from pydantic import BaseModel, EmailStr

class SignupSchema(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    password: str

    gender: str | None = None
    age: str | None = None
    state: str | None = None
    residence: str | None = None
    caste: str | None = None
    disability: str | None = None
    percentage: str | None = None
    minority: str | None = None
    is_student: str | None = None
    employment: str | None = None
    is_gov_employee: str | None = None
    is_bpl: str | None = None
    occupation: str | None = None
    annual_income: str | None = None
    family_income: str | None = None
    economic_distress: str | None = None


class LoginSchema(BaseModel):
    username: str
    password: str
class ChatRequest(BaseModel):
    message: str
