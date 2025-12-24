from fastapi import FastAPI
from db.db import Base, engine, get_db
import logging

# Initialize logging
logger = logging.getLogger("proj-task")

app = FastAPI(
    title="Proj_Task",
    description="api for proj_task",
    version="0.1.0",
)

# Create all tables at startup
Base.metadata.create_all(bind=engine)

@app.get('/')
def default():
    return{"msg": "Hello world"}