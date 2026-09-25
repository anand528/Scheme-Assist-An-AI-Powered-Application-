from sqlalchemy import Column, Integer, String
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    gender = Column(String)
    age = Column(String)
    state = Column(String)
    residence = Column(String)
    caste = Column(String)
    disability = Column(String)
    percentage = Column(String)
    minority = Column(String)
    is_student = Column(String)
    employment = Column(String)
    is_gov_employee = Column(String)
    is_bpl = Column(String)
    occupation = Column(String)
    annual_income = Column(String)
    family_income = Column(String)
    economic_distress = Column(String)
