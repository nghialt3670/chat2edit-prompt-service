from dotenv import load_dotenv

load_dotenv()

from api.v1 import chat, convs, files, users
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

app.include_router(chat.router)
app.include_router(files.router)
app.include_router(users.router)
app.include_router(convs.router)
