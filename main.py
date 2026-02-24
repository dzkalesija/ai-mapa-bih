from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List, Optional

# Database Setup
DATABASE_URL = "sqlite:///./ai_istrazivanje_v3.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class SurveyEntry(Base):
    __tablename__ = "istrazivanje_v3"
    id = Column(Integer, primary_key=True, index=True)
    entitet = Column(String)
    opcina = Column(String)
    struka = Column(String)
    pod_struka = Column(String, nullable=True) 
    specificni_odgovori = Column(Text, nullable=True) 
    alati = Column(String) 
    ustedjeno_vrijeme = Column(Integer)
    placa_pretplatu = Column(Boolean, default=False)
    uticaj_na_posao = Column(String)
    ai_iq_score = Column(Float)
    ip_adresa = Column(String, nullable=True) # NOVO: Čuvanje IP adrese

Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class SurveyCreate(BaseModel):
    entitet: str
    opcina: str
    struka: str
    pod_struka: Optional[str] = "Nije navedeno"
    specificni_odgovori: Optional[str] = ""
    alati: str
    ustedjeno_vrijeme: int
    placa_pretplatu: Optional[bool] = False
    uticaj_na_posao: str
    ai_iq_score: float

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"status": "AI Mapa BiH Backend V3.0 Aktivan", "message": "Sistem spreman za prijem podataka"}

@app.post("/submit-survey")
async def submit_survey(entry: SurveyCreate, request: Request, db: Session = Depends(get_db)):
    try:
        # Uzimanje IP adrese pošiljaoca
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        
        db_entry = SurveyEntry(
            **entry.dict(),
            ip_adresa=client_ip
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return {"status": "success", "id": db_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin-all")
def get_all(db: Session = Depends(get_db)):
    return db.query(SurveyEntry).all()