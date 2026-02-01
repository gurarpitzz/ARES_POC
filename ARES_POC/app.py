from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from verifier import Verifier
from typing import List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="ARES_POC: Research Verification Interface")

# Enable CORS for research-grade flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Research Verifier
# We initialize it once to benefit from model caching
verifier = Verifier(k=10, m=5, mode="web")

class ClaimRequest(BaseModel):
    claim: str
    k: int = 10
    m: int = 5

@app.post("/verify")
async def verify_claim(req: ClaimRequest):
    try:
        # Dynamically update parameters if requested
        verifier.k = req.k
        verifier.m = req.m
        
        result = verifier.verify(req.claim)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount Static Files (Frontend)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
