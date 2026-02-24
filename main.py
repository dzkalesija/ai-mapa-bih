from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import Optional

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
    specificni_odgovori = Column(Text)
    alati = Column(String)
    ustedjeno_vrijeme = Column(Integer)
    uticaj_na_posao = Column(String)
    ai_iq_score = Column(Float)

Base.metadata.create_all(bind=engine)

# Pydantic Schema
class SurveyCreate(BaseModel):
    entitet: str
    opcina: str
    struka: str
    specificni_odgovori: Optional[str] = ""
    alati: str
    ustedjeno_vrijeme: int
    uticaj_na_posao: str
    ai_iq_score: float

app = FastAPI()

# CORS - Dozvoljava pristup sa tvog sajta
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

@app.post("/submit-survey")
async def submit_survey(entry: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_entry = SurveyEntry(**entry.dict())
        db.add(db_entry)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin-all")
def get_all(db: Session = Depends(get_db)):
    return db.query(SurveyEntry).all()

@app.get("/")
def home():
    return {"status": "Online"}