from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from predictor import (
    predict_exam_score,
    generate_shap_explanation
)
from database import engine, SessionLocal
from models import Base, Student, AcademicRecord

app = FastAPI()

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "attendance": 0,
            "predicted_gpa": 0,
            "health_score": 0,
            "risk_level": "Not Available"
        }
    )
@app.get("/student-data", response_class=HTMLResponse)
def student_data_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_data.html"
    )
@app.get("/student-data-ai", response_class=HTMLResponse)
def student_data_ai_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_data_ai.html"
    )
@app.post("/register")
def register_student(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    existing_student = db.query(Student).filter(
        Student.email == email
    ).first()

    if existing_student:
        db.close()
        return {"message": "Email already registered"}

    student = Student(
        name=name,
        email=email,
        password=password
    )

    db.add(student)
    db.commit()
    db.close()

    return RedirectResponse(
        url="/login",
        status_code=303
    )


@app.post("/login")
def login_student(
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    student = db.query(Student).filter(
        Student.email == email
    ).first()

    db.close()

    if student and student.password == password:
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return {"message": "Invalid Email or Password"}
@app.post("/save-data")
def save_data(
    request: Request,
    name: str = Form(...),
    attendance: float = Form(...),
    mid1: float = Form(...),
    mid2: float = Form(...),
    weekly: float = Form(...),
    assignment: float = Form(...),
    lab: float = Form(...),
    study_hours: float = Form(...),
    backlogs: int = Form(...)
):

    health_score = (
        attendance * 0.20 +
        ((mid1 + mid2)/50)*100 * 0.30 +
        (weekly/5)*100 * 0.10 +
        (assignment/10)*100 * 0.10 +
        (lab/30)*100 * 0.20 +
        (study_hours/10)*100 * 0.10
    )
    health_score -= backlogs * 5

    health_score = max(0, min(100, health_score))
    predicted_gpa = round(
        (health_score/100)*10,
        2
    )

    if health_score >= 80:
        risk_level = "LOW"

    elif health_score >= 60:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    db = SessionLocal()

    record = AcademicRecord(
        student_name=name,
        attendance=attendance,
        mid1=mid1,
        mid2=mid2,
        weekly=weekly,
        assignment=assignment,
        lab=lab,
        study_hours=study_hours,
        backlogs=backlogs,
        health_score=health_score,
        predicted_gpa=predicted_gpa,
        risk_level=risk_level
    )

    db.add(record)
    db.commit()
    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "attendance": attendance,
            "predicted_gpa": predicted_gpa,
            "health_score": round(health_score, 2),
            "risk_level": risk_level
        }
    )
@app.post("/predict-ai")
def predict_ai(
    request: Request,
    Hours_Studied: int = Form(...),
    Attendance: int = Form(...),
    Parental_Involvement: str = Form(...),
    Access_to_Resources: str = Form(...),
    Extracurricular_Activities: str = Form(...),
    Sleep_Hours: int = Form(...),
    Previous_Scores: int = Form(...),
    Motivation_Level: str = Form(...),
    Internet_Access: str = Form(...),
    Tutoring_Sessions: int = Form(...),
    Family_Income: str = Form(...),
    Teacher_Quality: str = Form(...),
    Peer_Influence: str = Form(...),
    Physical_Activity: int = Form(...),
    Learning_Disabilities: str = Form(...),
    Parental_Education_Level: str = Form(...),
    Distance_from_Home: str = Form(...),
    School_Type: str = Form(...),
    Gender: str = Form(...)
):

    student_data = {
        "Hours_Studied": Hours_Studied,
        "Attendance": Attendance,
        "Parental_Involvement": Parental_Involvement,
        "Access_to_Resources": Access_to_Resources,
        "Extracurricular_Activities": Extracurricular_Activities,
        "Sleep_Hours": Sleep_Hours,
        "Previous_Scores": Previous_Scores,
        "Motivation_Level": Motivation_Level,
        "Internet_Access": Internet_Access,
        "Tutoring_Sessions": Tutoring_Sessions,
        "Family_Income": Family_Income,
        "Teacher_Quality": Teacher_Quality,
        "Peer_Influence": Peer_Influence,
        "Physical_Activity": Physical_Activity,
        "Learning_Disabilities": Learning_Disabilities,
        "Parental_Education_Level": Parental_Education_Level,
        "Distance_from_Home": Distance_from_Home,
        "School_Type": School_Type,
        "Gender": Gender
    }

    predicted_score = predict_exam_score(student_data)
    shap_explanations = generate_shap_explanation(
        student_data
    )
    if predicted_score >= 80:
        risk_level = "LOW"
        mentor_message = (
            "Excellent performance! Maintain your current study habits and continue participating actively in academics."
        )

    elif predicted_score >= 60:
        risk_level = "MEDIUM"
        mentor_message = (
            "Good performance, but there is room for improvement. Increase study consistency and seek additional guidance when needed."
        )

    else:
        risk_level = "HIGH"
        mentor_message = (
            "Immediate intervention is recommended. Increase study hours, improve attendance, and utilize tutoring support."
        )
 
    return templates.TemplateResponse(
        request=request,
        name="ai_result.html",
        context={
            "predicted_score": predicted_score,
            "risk_level": risk_level,
            "mentor_message": mentor_message,
            "shap_explanations": shap_explanations
        }
)