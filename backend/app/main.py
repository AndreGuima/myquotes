from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.quotes import router as quotes_router

app = FastAPI(title="MyQuotes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quotes_router)
