from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import pandas as pd
from fastapi import HTTPException
from datetime import datetime
from fastapi.testclient import TestClient

app = FastAPI(
    title="Pointages API",
    description="API exposing time logs from CSV file",
    version="1.0.0"
)

# Enable public access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # open to all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure DataFrame is always initialized with correct columns
import os
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

# Pydantic model
class Pointage(BaseModel):
    start: str | None = None
    name: str
    type_sollicitation: str
    practice: str | None = None
    director: str | None = None
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


@app.get("/pointages", response_model=list[Pointage])
def get_pointages():
    # Ensure all columns exist
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = None
    # Convert NaN to None for JSON serialization
    records = df[COLUMNS].where(pd.notnull(df[COLUMNS]), None).to_dict(orient="records")
    # Ensure type_sollicitation is always a string
    for rec in records:
        if rec["type_sollicitation"] is None:
            rec["type_sollicitation"] = "none"
    return records

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
        df.to_csv("pointages-cb.csv", sep=";", index=False)
        return new_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding record: {str(e)}")

