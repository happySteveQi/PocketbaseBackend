from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from models.user import *
from models.note import *
from request.user import router as user_router
from request.note import router as note_router

app = FastAPI()

@app.get("/")
async def root():
    return {"hello":"fastapi"}
    
app.include_router(user_router)
app.include_router(note_router)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=6000)