from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
import os

# TVOJ POSTGRES URL
DB_URL = "postgresql://ai_monitor_db_1ehj_user:nTFVcK3Shj025wspUuOiGoMaPeTRCHwf@dpg-d6eqrb3h46gs73e9dr60-a.frankfurt-postgres.render.com/ai_monitor_db_1ehj"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DEFINICIJA TABELE
class SurveyEntry(Base):
    __tablename__ = "istrazivanje_trajno_final"
    id = Column(Integer, primary_key=True, index=True)
    entitet = Column(String)
    opcina = Column(String)
    sektor = Column(String)
    pod_sektor = Column(String)
    odgovori = Column(Text)
    alati = Column(String)
    usteda = Column(Integer)
    stav = Column(String)
    score = Column(Float)

# Kreiranje tabele na Postgresu odmah pri pokretanju
Base.metadata.create_all(bind=engine)

# VALIDACIJA PODATAKA
class SurveyCreate(BaseModel):
    entitet: str
    opcina: str
    sektor: str
    pod_sektor: str
    odgovori: str
    alati: str
    usteda: int
    stav: str
    score: float

app = FastAPI()

# DOZVOLA PRISTUPA (CORS)
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
    return {"status": "Online", "database": "PostgreSQL Frankfurt Connected"}

@app.post("/submit-survey")
async def create_entry(survey: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_entry = SurveyEntry(**survey.dict())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return {"status": "success", "id": db_entry.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin-all")
async def get_all(db: Session = Depends(get_db)):
    # Vraća sve unose poredane tako da najnoviji bude prvi
    return db.query(SurveyEntry).order_by(SurveyEntry.id.desc()).all()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)