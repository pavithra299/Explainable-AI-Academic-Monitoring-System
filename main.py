from datetime import date
from fastapi import FastAPI, Request, Form
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from predictor import (
    predict_exam_score,
    generate_shap_explanation
)
from database import engine, SessionLocal
from models import (
    Base,
    Student,
    AcademicRecord,
    PredictionHistory,
    Admin
)
app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="academic_monitoring_secret"
)

templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )
@app.get("/student-register", response_class=HTMLResponse)
def student_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_register.html"
    )


@app.get("/student-login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_login.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):

    student_email = request.cookies.get(
        "student_email"
    )

    db = SessionLocal()

    latest_prediction = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.student_email == student_email
    ).order_by(
        PredictionHistory.id.desc()
    ).first()
    total_predictions = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.student_email == student_email
    ).count()

    db.close()

    if latest_prediction:

        predicted_score = (
            latest_prediction.predicted_score
        )

        risk_level = (
            latest_prediction.risk_level
        )

        prediction_date = (
            latest_prediction.prediction_date
        )

    else:

        predicted_score = 0

        risk_level = "Not Available"

        prediction_date = "No Predictions Yet"
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "predicted_score": predicted_score,
            "risk_level": risk_level,
            "prediction_date": prediction_date,
            "total_predictions": total_predictions
        }
    )
@app.get("/student-data", response_class=HTMLResponse)
def student_data_page(request: Request):
    return RedirectResponse(
        url="/dashboard",
        status_code=303
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
        url="/student-login",
        status_code=303
    )


@app.post("/student-login")
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

        response = RedirectResponse(
            url="/dashboard",
            status_code=303
        )

        response.set_cookie(
            key="student_email",
            value=student.email
        )

        return response

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
            "predicted_score": predicted_score,
            "risk_level": risk_level,
            "prediction_date": prediction_date,
            "total_predictions": total_predictions
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
    student_email = request.cookies.get(
        "student_email"
    )

    db = SessionLocal()

    prediction = PredictionHistory(
        student_email=student_email,
        predicted_score=predicted_score,
        risk_level=risk_level,
        prediction_date=str(date.today())
    )

    db.add(prediction)

    db.commit()

    db.close()
 
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

@app.post("/ask-mentor")
def ask_mentor(
    request: Request,
    question: str = Form(...)
):

    student_email = request.cookies.get(
        "student_email"
    )

    db = SessionLocal()

    latest_prediction = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.student_email == student_email
    ).order_by(
        PredictionHistory.id.desc()
    ).first()

    db.close()

    if latest_prediction:

        score = latest_prediction.predicted_score
        risk = latest_prediction.risk_level

    else:

        score = 0
        risk = "HIGH"

    question = question.lower()

    if "improve" in question:

        if risk == "HIGH":

            response = (
                f"Your predicted score is {score}. "
                "Focus on improving attendance, increasing study hours, "
                "and attending tutoring sessions regularly."
            )

        elif risk == "MEDIUM":

            response = (
                f"Your predicted score is {score}. "
                "You are performing reasonably well. "
                "Maintain consistency and strengthen weak subjects."
            )

        else:

            response = (
                f"Excellent work! Your predicted score is {score}. "
                "Continue your current study habits."
            )

    elif "attendance" in question:

        response = (
            "Maintain attendance above 80% to improve academic outcomes."
        )

    elif "study" in question:

        response = (
            "Aim for at least 10–15 focused study hours each week."
        )

    else:

        response = (
            "Try asking questions like: "
            "'How can I improve?', "
            "'How important is attendance?', "
            "'How should I study effectively?'"
        )

    return {
        "response": response
    }

@app.post("/predict-gpa")
def predict_gpa(
    attendance: float = Form(...),
    internal_marks: float = Form(...)
):

    internal_percent = (
        internal_marks / 30
    ) * 100

    health_score = (
        attendance * 0.4 +
        internal_percent * 0.6
    )

    predicted_gpa = round(
        (health_score / 100) * 10,
        2
    )

    if predicted_gpa >= 9:

        suggestion = (
            "Excellent performance. Maintain your consistency."
        )

    elif predicted_gpa >= 7:

        suggestion = (
            "Good progress. Improve internal marks slightly to achieve distinction."
        )

    elif predicted_gpa >= 5:

        suggestion = (
            "Increase attendance and focus more on internal assessments."
        )

    else:

        suggestion = (
            "Immediate intervention recommended. Meet faculty mentors and develop a structured study plan."
        )

    return {
        "gpa": predicted_gpa,
        "suggestion": suggestion
    }




@app.get("/prediction-history", response_class=HTMLResponse)
def prediction_history(
    request: Request
):
    student_email = request.cookies.get(
        "student_email"
    )

    db = SessionLocal()

    predictions = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.student_email == student_email
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="prediction_history.html",
        context={
            "predictions": predictions
        }
    )
@app.get("/admin-dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):

    db = SessionLocal()

    total_predictions = db.query(
        PredictionHistory
    ).count()

    predictions = db.query(
        PredictionHistory
    ).all()

    if predictions:

        average_score = round(
            sum(
                prediction.predicted_score
                for prediction in predictions
            ) / len(predictions),
            2
        )

    else:

        average_score = 0

    high_risk = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.risk_level == "HIGH"
    ).count()
    medium_risk = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.risk_level == "MEDIUM"
    ).count()

    low_risk = db.query(
        PredictionHistory
    ).filter(
        PredictionHistory.risk_level == "LOW"
    ).count()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "total_predictions": total_predictions,
            "average_score": average_score,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }
    )
@app.get("/admin-register", response_class=HTMLResponse)
def admin_register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin_register.html"
    )


@app.post("/admin-register")
def admin_register(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    access_code: str = Form(...)
):

    if access_code != "VIIT2026ADMIN":
        return {
            "message": "Invalid Admin Access Code"
        }

    db = SessionLocal()

    existing_admin = db.query(
        Admin
    ).filter(
        Admin.email == email
    ).first()

    if existing_admin:

        db.close()

        return {
            "message": "Admin already exists"
        }

    admin = Admin(
        name=name,
        email=email,
        password=password
    )

    db.add(admin)

    db.commit()

    db.close()

    return RedirectResponse(
        url="/admin-login",
        status_code=303
    )
@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin_login.html"
    )
@app.post("/admin-login")
def admin_login(
    email: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    admin = db.query(
        Admin
    ).filter(
        Admin.email == email
    ).first()

    db.close()

    if admin and admin.password == password:

        return RedirectResponse(
            url="/admin-dashboard",
            status_code=303
        )

    return {
        "message": "Invalid Admin Credentials"
    }