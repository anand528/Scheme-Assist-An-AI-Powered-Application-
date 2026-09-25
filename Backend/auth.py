from passlib.context import CryptContext
from sqlalchemy.orm import Session
from backend.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, data):
    user = User(
        full_name=data.full_name,
        username=data.username,
        email=data.email,
        password=hash_password(data.password),

        gender=data.gender,
        age=data.age,
        state=data.state,
        residence=data.residence,
        caste=data.caste,
        disability=data.disability,
        percentage=data.percentage,
        minority=data.minority,
        is_student=data.is_student,
        employment=data.employment,
        is_gov_employee=data.is_gov_employee,
        is_bpl=data.is_bpl,
        occupation=data.occupation,
        annual_income=data.annual_income,
        family_income=data.family_income,
        economic_distress=data.economic_distress
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
