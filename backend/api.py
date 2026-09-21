from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from pipeline import process_email


app = FastAPI(
    title="ShipCheck AI API",
    version="1.0.0",
    description="Shipping Instruction and Draft Bill of Lading verification API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://localhost:3000",
        "https://127.0.0.1:3000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    email_id: str = Field(..., min_length=1)


@app.get("/")
def root():
    return {
        "service": "ShipCheck AI API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
def analyze_email(request: AnalyzeRequest):
    try:
        result = process_email(request.email_id)
        return result

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {e}",
        )
