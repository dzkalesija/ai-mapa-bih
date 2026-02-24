from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List

# DATABASE SETUP
# Koristimo check_same_thread=False jer SQLite i FastAPI rade u više threadova
SQLALCHEMY_DATABASE_URL = "sqlite:///./ai_monitor_bih.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MODEL BAZE PODATAKA (SQLAlchemy)
class SurveyEntry(Base):
    __tablename__ = "istrazivanje_final" # Promijenili smo ime da se baza automatski rekreira sa novim kolonama
    id = Column(Integer, primary_key=True, index=True)
    entitet = Column(String)
    opcina = Column(String)
    sektor = Column(String)
    pod_sektor = Column(String)  # KLJUČNO: Dodata podrška za pod-sektore
    odgovori = Column(Text)       # Detaljna pitanja
    alati = Column(String)
    usteda = Column(Integer)
    stav = Column(String)
    score = Column(Float)

# Kreiranje tabela
Base.metadata.create_all(bind=engine)

# PYDANTIC SCHEMAS (Za validaciju dolaznih podataka)
class SurveyCreate(BaseModel):
    entitet: str
    opcina: str
    sektor: str
    pod_sektor: str  # Mora se podudarati sa index.html
    odgovori: str
    alati: str
    usteda: int
    stav: str
    score: float

app = FastAPI()

# CORS POSTAVKE (Dozvoli pristup sa tvog GitHub-a ili lokalnog računara)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency za bazu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# RUTA ZA UPIS PODATAKA (Iz index.html)
@app.post("/submit-survey")
async def create_entry(survey: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_entry = SurveyEntry(
            entitet=survey.entitet,
            opcina=survey.opcina,
            sektor=survey.sektor,
            pod_sektor=survey.pod_sektor,
            odgovori=survey.odgovori,
            alati=survey.alati,
            usteda=survey.usteda,
            stav=survey.stav,
            score=survey.score
        )
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return {"status": "success", "id": db_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# RUTA ZA ADMIN PANEL (Iz admin.html)
@app.get("/admin-all")
async def get_all_entries(db: Session = Depends(get_db)):
    entries = db.query(SurveyEntry).all()
    return entries

# ROOT RUTA (Za provjeru da li server radi)
@app.get("/")
def home():
    return {"message": "AI Monitor BiH API je online"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)