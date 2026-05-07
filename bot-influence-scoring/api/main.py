from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import scores, nodes
from api.db.session import load_precomputed_data

app = FastAPI(
    title="Bot-Aware Influence Scoring API",
    description="REST API for exploring bot detection results and sanitized influence scores.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    load_precomputed_data()

@app.get("/")
async def root():
    return {"message": "Welcome to the Bot-Aware Influence Scoring API. Visit /docs for Swagger UI."}

# Include routers
app.include_router(scores.router, prefix="/api/v1/scores", tags=["Scores"])
app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["Nodes"])
