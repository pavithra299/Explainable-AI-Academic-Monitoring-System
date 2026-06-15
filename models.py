from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy import Float, ForeignKey

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True)

    student_name = Column(String)

    attendance = Column(Float)

    mid1 = Column(Float)

    mid2 = Column(Float)

    weekly = Column(Float)

    assignment = Column(Float)

    lab = Column(Float)

    study_hours = Column(Float)

    backlogs = Column(Integer)

    health_score = Column(Float)

    predicted_gpa = Column(Float)

    risk_level = Column(String)
class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)

    student_email = Column(String)

    predicted_score = Column(Float)

    risk_level = Column(String)

    prediction_date = Column(String)
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    email = Column(String, unique=True)

    password = Column(String)

    role = Column(String, default="Faculty")