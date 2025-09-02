from fastapi import FastAPI

from config import Config

settings = Config
settings.setup()

app = FastAPI()


@app.get("/")
def root():
    return {"Test": "Success"}
