import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import jobs, applications, stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AAJAS API", description="Agentic Autonomous Job Application System API", version="0.1.0")

# CORS
origins = [
    "http://localhost:3000", # Next.js
    "http://localhost:8000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])

@app.get("/")
async def root():
    return {"message": "AAJAS API is running"}
