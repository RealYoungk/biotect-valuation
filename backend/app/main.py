from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import valuation, analysis, companies
from app.core.config import settings

app = FastAPI(
    title="Biotect Valuation API",
    description="AI-powered biotech company valuation system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(companies.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])  
app.include_router(valuation.router, prefix="/api/v1/valuation", tags=["valuation"])

@app.get("/")
async def root():
    return {"message": "Biotect Valuation API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}