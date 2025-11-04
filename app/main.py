from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api.v1.complaints_controller import router as complaints_router

import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully.")

    yield  # Application runs here

    # Shutdown
    await engine.dispose()
    print("Database connection closed.")


app = FastAPI(
    title="Smart City Complaint API",
    version="1.0.0",
    lifespan=lifespan,
    debug=True
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "trace": tb},
        )
        
# Routers
app.include_router(complaints_router, prefix="/api/v1/complaints", tags=["Complaints"])


@app.get("/")
async def root():
    print("Smart City API is running")
    return {"message": "Smart City API is running"}
