from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import settings
from app.routes import (
    authn
    
)
from starlette.middleware.sessions import SessionMiddleware
from app.middleware.access_middle import (
    ProcessTimeMiddleware,
    AccessCheckMiddleware,
    RequestLoggingMiddleware
)


app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    SessionMiddleware,
    secret_key="a7b8c9d10e11f12a13b14c15d16e17f18a19b20c21d22e23f24b25c26d27e28f",
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "localhost:8000"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(AccessCheckMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authn.router, tags=["Authentication"], prefix="/api/authn")


@app.get("/index")
def root():
    return {"message": "Welcome to FastAPI with MongoDB"}


##