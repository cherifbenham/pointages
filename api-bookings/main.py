from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# --- API setup ---
app = FastAPI(
    title="Pointages API",
    description="API exposing time logs from CSV file",
    version="1.0.0"
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open to all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Key Enforcement ---
EXPECTED_API_KEY = os.getenv("API_KEY")

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    client_key = request.headers.get("x-api-key")
    if EXPECTED_API_KEY and client_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return await call_next(request)

# --- CSV and DataFrame Initialization ---
CSV_PATH = "pointages-cb.csv"
COLUMNS = [
    "start", 
    "name", 
    "type_sollicitation", 
    "practice", 
    "director", 
    "client",
    "department", 
    "kam", 
    "business_manager", 
    "description",
    "confirmed"
]

if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
    df = pd.read_csv(CSV_PATH, sep=";")
else:
    df = pd.DataFrame(columns=COLUMNS)

# --- Pydantic model ---
class Pointage(BaseModel):
    start: str | None = None
    name: str
    type_sollicitation: str
    practice: str | None = None # email - practice
    director: str | None = None # kam - director
    client: str | None = None
    department: str | None = None
    kam: str | None = None
    business_manager: str | None = None
    description: str | None = None
    confirmed: bool | None = None

    @field_validator("start", mode="before")
    @classmethod
    def set_start_now(cls, v):
        return v or datetime.now().strftime("%m/%d/%y %H:%M:%S")
    
    @field_validator("confirmed", mode="before")
    @classmethod
    def parse_confirmed(cls, v):
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ["true", "1", "yes"]

# --- Endpoints ---
@app.get("/pointages", response_model=list[Pointage])
def get_pointages():
    # Use Pointage class keys for columns
    pointage_keys = list(Pointage.model_fields.keys())
    for col in pointage_keys:
        if col not in df.columns:
            df[col] = None
    records = df[pointage_keys].where(pd.notnull(df[pointage_keys]), None).to_dict(orient="records")
    # validated = guaranteed clean
    validated = [Pointage(**rec).model_dump() for rec in records]
    return validated

@app.post("/pointages", response_model=Pointage)
def post_pointage(pointage: Pointage):
    global df
    try:
        new_record = {
            "start": pointage.start or datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            "name": pointage.name,
            "type_sollicitation": pointage.type_sollicitation,
            "practice": pointage.practice or "none",
            "director": pointage.director or "none",
            "client": pointage.client or "none",
            "department": pointage.department or "none",
            "kam": pointage.kam or "none",
            "business_manager": pointage.business_manager or "none",
            "description": pointage.description or "none",
            "confirmed": pointage.confirmed or False
        }
        new_df = pd.DataFrame([new_record])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(CSV_PATH, sep=";", index=False)
        return new_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding record: {str(e)}")