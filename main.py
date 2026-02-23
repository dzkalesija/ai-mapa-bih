from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List

# Konfiguracija baze
SQLALCHEMY_DATABASE_URL = "sqlite:///./ai_istrazivanje_final.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model baze podataka
class SurveyEntry(Base):
    __tablename__ = "velika_anketa"
    id = Column(Integer, primary_key=True, index=True)
    entitet = Column(String)
    opcina = Column(String)
    struka = Column(String)
    obrazovanje = Column(String)
    koristi_tekst = Column(Boolean)
    koristi_slike = Column(Boolean)
    koristi_kod = Column(Boolean)
    koristi_video = Column(Boolean)
    frekvencija = Column(String)
    ustedjeno_vrijeme = Column(Integer)
    placa_pretplatu = Column(Boolean)
    vjeruje_odgovorima = Column(Integer)
    strah_faktor = Column(Integer)
    ai_iq_score = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic shema za validaciju dolaznih podataka
class SurveyRequest(BaseModel):
    entitet: str
    opcina: str
    struka: str
    obrazovanje: str
    koristi_tekst: bool
    koristi_slike: bool
    koristi_kod: bool
    koristi_video: bool
    frekvencija: str
    ustedjeno_vrijeme: int
    placa_pretplatu: bool
    vjeruje_odgovorima: int
    strah_faktor: int

app = FastAPI(title="AI Istraživanje BiH 2026")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/submit-survey")
def submit_survey(req: SurveyRequest, db: Session = Depends(get_db)):
    # Napredni AI IQ Algoritam
    score = 0
    if req.koristi_tekst: score += 15
    if req.koristi_slike: score += 20
    if req.koristi_kod: score += 25
    if req.koristi_video: score += 30
    score += (req.ustedjeno_vrijeme / 2)
    if req.placa_pretplatu: score += 40
    score += (req.vjeruje_odgovorima * 5)
    
    new_entry = SurveyEntry(
        entitet=req.entitet, opcina=req.opcina, struka=req.struka,
        obrazovanje=req.obrazovanje, koristi_tekst=req.koristi_tekst,
        koristi_slike=req.koristi_slike, koristi_kod=req.koristi_kod,
        koristi_video=req.koristi_video, frekvencija=req.frekvencija,
        ustedjeno_vrijeme=req.ustedjeno_vrijeme, placa_pretplatu=req.placa_pretplatu,
        vjeruje_odgovorima=req.vjeruje_odgovorima, strah_faktor=req.strah_faktor,
        ai_iq_score=score
    )
    db.add(new_entry)
    db.commit()
    return {"status": "success", "score": score}

@app.get("/admin-all")
def get_all(db: Session = Depends(get_db)):
    return db.query(SurveyEntry).all()

@app.get("/dashboard-stats")
def get_stats(db: Session = Depends(get_db)):
    all_data = db.query(SurveyEntry).all()
    if not all_data: return {"ukupno": 0}
    avg_iq = sum(d.ai_iq_score for d in all_data) / len(all_data)
    return {"ukupno": len(all_data), "prosecan_iq": round(avg_iq, 2)}