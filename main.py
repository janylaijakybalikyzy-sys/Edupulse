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

# 0. БАШКЫ БЕТ (Сайтка киргенде автоматтык түрдө мугалимдин бетине жөнөтөт)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return RedirectResponse(url="/teacher")

# --- СТУДЕНТТЕР ҮЧҮН ---

# 1. Студент добуш бере турган бет (ар бир сабак үчүн уникалдуу ID менен)
@app.get("/vote/{sub_id}", response_class=HTMLResponse)
async def vote_page(request: Request, sub_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == sub_id).first()
    if not subject:
        return HTMLResponse("<h2>Кечириңиз, мындай сабак табылган жок.</h2>", status_code=404)
    return templates.TemplateResponse("index.html", {"request": request, "subject": subject})

# 2. Студенттин пикирин базага сактоо
@app.post("/submit/{sub_id}")
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
        <div style="text-align:center; padding:50px; font-family:sans-serif;">
            <h2 style="color: #27ae60;">Рахмат! Пикириңиз кабыл алынды. ✅</h2>
            <p>Сиз терезени жапсаңыз болот.</p>
        </div>
    """)


# --- МУГАЛИМДЕР ҮЧҮН ---

# 1. Мугалим сабак каттай турган бет
@app.get("/teacher", response_class=HTMLResponse)
async def teacher_home(request: Request):
    return templates.TemplateResponse("teacher.html", {"request": request})

# 2. Жаңы сабак түзүү логикасы
@app.post("/create_subject")
async def create_subject(name: str = Form(...), teacher_name: str = Form(...), db: Session = Depends(get_db)):
    # 1. Текшеребиз: Бул сабак мурун түзүлгөнбү?
    existing_subject = db.query(models.Subject).filter(models.Subject.name == name).first()
    
    if existing_subject:
        # 2. Эгер бар болсо, жаңы түзбөй эле ошол эскисинин бетине жөнөтөбүз
        return RedirectResponse(url=f"/dashboard/{existing_subject.id}", status_code=303)
    
    # 3. Эгер жок болсо, жаңы сабак түзөбүз
    new_subject = models.Subject(name=name, teacher_name=teacher_name)
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    return RedirectResponse(url=f"/dashboard/{new_subject.id}", status_code=303)

# 3. Мугалимдин аналитикалык панели (Ар бир сабак үчүн өзүнчө)
@app.get("/dashboard/{sub_id}", response_class=HTMLResponse)
async def dashboard(request: Request, sub_id: int, db: Session = Depends(get_db)):
    subject = db.query(models.Subject).filter(models.Subject.id == sub_id).first()
    if not subject:
        return HTMLResponse("Сабак табылган жок", status_code=404)
        
    feedbacks = subject.feedbacks
    total = len(feedbacks)
    avg_rating = sum(f.rating for f in feedbacks) / total if total > 0 else 0
    
    counts = [0, 0, 0, 0, 0]
    for f in feedbacks:
        if 1 <= f.rating <= 5:
            counts[f.rating - 1] += 1
            
    # Студенттерге бериле турган шилтеме (Мугалим ушуну көчүрүп берет)
    student_link = f"https://edupulse-janylai.onrender.com/vote/{sub_id}"

    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "subject": subject, 
        "total": total, 
        "avg": round(avg_rating, 1), 
        "counts": counts, 
        "student_link": student_link,
        "feedbacks": feedbacks
    })