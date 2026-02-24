from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
import os

# DATABASE SETUP
SQLALCHEMY_DATABASE_URL = "sqlite:///./ai_monitor_final.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MODEL BAZE - Mora imati pod_sektor
class SurveyEntry(Base):
    __tablename__ = "istrazivanje_v12" # Promjena imena kreira svježu tabelu
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

Base.metadata.create_all(bind=engine)

# SCHEMAS
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

# CORS - Dozvoljava index.html i admin.html komunikaciju
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
def read_root():
    return {"status": "Online", "version": "2.0.DeepSector"}

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
        print(f"ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin-all")
async def get_all(db: Session = Depends(get_db)):
    return db.query(SurveyEntry).all()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)