from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine

# Базаны түзүү (таблицалар жок болсо, автоматтык түрдө жаратат)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# База менен байланыш функциясы
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 0. БАШКЫ БЕТ
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return RedirectResponse(url="/teacher")

# --- СТУДЕНТТЕР ҮЧҮН ---

# 1. Студент добуш бере турган баракчаны ачуу (GET)
@app.get("/vote/{sub_id}", response_class=HTMLResponse)
async def vote_page(request: Request, sub_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == sub_id).first()
    if not subject:
        return RedirectResponse(url="/teacher")
    return templates.TemplateResponse("index.html", {"request": request, "subject": subject})

# 2. Студенттин пикирин кабыл алуу жана базага сактоо (POST)
@app.post("/vote/{sub_id}")
async def create_feedback(
    sub_id: int,
    rating: int = Form(...), 
    difficulty: str = Form(None), 
    db: Session = Depends(get_db)
):
    new_feedback = models.Feedback(
        subject_id=sub_id, 
        rating=rating, 
        difficulty=difficulty
    )
    db.add(new_feedback)
    db.commit()
    
    return HTMLResponse("""
        <div style="text-align:center; padding:50px; font-family:sans-serif; background-color: #f8f9fa; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <h2 style="color: #27ae60;">Рахмат! Пикириңиз кабыл алынды. ✅</h2>
            <p style="font-size: 18px; color: #555;">Сиздин бааңыз ийгиликтүү сакталды.</p>
            <br>
            <a href="/teacher" style="text-decoration: none; color: #3498db; font-weight: bold; border: 1px solid #3498db; padding: 10px 20px; border-radius: 5px;">Башкы бетке өтүү</a>
        </div>
    """)


# --- МУГАЛИМДЕР ҮЧҮН ---

# 1. Мугалим сабак каттай турган бет
@app.get("/teacher", response_class=HTMLResponse)
async def teacher_home(request: Request):
    return templates.TemplateResponse("teacher.html", {"request": request})

# 2. Жаңы сабак түзүү
@app.post("/create_subject")
async def create_subject(
    name: str = Form(...), 
    teacher_name: str = Form(...), 
    topic_name: str = Form(...), 
    lesson_date: str = Form(...), 
    db: Session = Depends(get_db)
):
    new_subject = models.Subject(
        name=name, 
        teacher_name=teacher_name,
        topic_name=topic_name,
        lesson_date=lesson_date
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return RedirectResponse(url=f"/dashboard/{new_subject.id}", status_code=303)

# 3. Мугалимдин аналитикалык панели (Dashboard)
@app.get("/dashboard/{sub_id}", response_class=HTMLResponse)
async def dashboard(request: Request, sub_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == sub_id).first()
    
    if not subject:
        return RedirectResponse(url="/teacher")
        
    feedbacks = subject.feedbacks
    total = len(feedbacks)
    avg_rating = sum(f.rating for f in feedbacks) / total if total > 0 else 0
    
    counts = [0, 0, 0, 0, 0]
    for f in feedbacks:
        if 1 <= f.rating <= 5:
            counts[f.rating - 1] += 1
            
    # ШИЛТЕМЕНИ АВТОМАТТЫК ТҮРДӨ ТҮЗҮҮ (Эң коопсуз жолу)
    actual_base_url = str(request.base_url).rstrip("/")
    student_link = f"{actual_base_url}/vote/{sub_id}"

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "subject": subject, 
        "total": total, 
        "avg": round(avg_rating, 1), 
        "counts": counts, 
        "student_link": student_link,
        "feedbacks": feedbacks
    })