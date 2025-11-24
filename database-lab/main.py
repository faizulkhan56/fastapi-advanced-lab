from fastapi import FastAPI, Depends, HTTPException
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import sys

from database import SessionLocal, engine, Base
import models, schemas
from utils.logger import logger
from utils.exception import CustomException

# Create the database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")
    raise CustomException(f"Database initialization error: {str(e)}", sys)

app = FastAPI(title="Database Lab - Todos API")
logger.info("Database Lab application started")

# Global exception handler for CustomException
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    logger.error(f"CustomException raised: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": "CustomException"}
    )

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise CustomException(f"Database session error: {str(e)}", sys)
    finally:
        db.close()
        logger.debug("Database session closed")


@app.post("/todos/", response_model=schemas.Todo)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Creating todo: {todo.title}")
        db_todo = models.Todo(**todo.dict())
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Todo created successfully with ID: {db_todo.id}")
        return db_todo
    except Exception as e:
        logger.error(f"Error creating todo: {str(e)}")
        db.rollback()
        raise CustomException(f"Error creating todo: {str(e)}", sys)


@app.get("/todos/{todo_id}", response_model=schemas.Todo)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Reading todo with ID: {todo_id}")
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if not todo:
            logger.warning(f"Todo with ID {todo_id} not found")
            raise HTTPException(status_code=404, detail="Todo not found")
        logger.info(f"Todo {todo_id} retrieved successfully")
        return todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading todo {todo_id}: {str(e)}")
        raise CustomException(f"Error reading todo: {str(e)}", sys)


@app.put("/todos/{todo_id}", response_model=schemas.Todo)
def update_todo(todo_id: int, todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Updating todo with ID: {todo_id}")
        db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if not db_todo:
            logger.warning(f"Todo with ID {todo_id} not found for update")
            raise HTTPException(status_code=404, detail="Todo not found")
        for key, value in todo.dict().items():
            setattr(db_todo, key, value)
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Todo {todo_id} updated successfully")
        return db_todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {str(e)}")
        db.rollback()
        raise CustomException(f"Error updating todo: {str(e)}", sys)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Deleting todo with ID: {todo_id}")
        todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if not todo:
            logger.warning(f"Todo with ID {todo_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Todo not found")
        db.delete(todo)
        db.commit()
        logger.info(f"Todo {todo_id} deleted successfully")
        return {"detail": "Todo deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {str(e)}")
        db.rollback()
        raise CustomException(f"Error deleting todo: {str(e)}", sys)


@app.get("/todos/", response_model=List[schemas.Todo])
def read_todos(db: Session = Depends(get_db)):
    try:
        logger.info("Reading all todos")
        todos = db.query(models.Todo).all()
        logger.info(f"Retrieved {len(todos)} todos")
        return todos
    except Exception as e:
        logger.error(f"Error reading todos: {str(e)}")
        raise CustomException(f"Error reading todos: {str(e)}", sys)


@app.post("/todos/background/")
def create_todo_background(
    todo: schemas.TodoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    def process_todo(todo_data: dict):
        # Simulate long running task
        import time
        try:
            logger.info(f"Processing todo in background: {todo_data.get('title', 'Unknown')}")
            time.sleep(2)
            logger.info(f"Background processing completed for todo: {todo_data.get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Error in background task: {str(e)}")

    try:
        logger.info(f"Creating todo with background processing: {todo.title}")
        db_todo = models.Todo(**todo.dict())
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        logger.info(f"Todo created with ID: {db_todo.id}, background task scheduled")

        background_tasks.add_task(process_todo, todo.dict())
        return {"message": "Todo created, processing in background"}
    except Exception as e:
        logger.error(f"Error creating todo with background task: {str(e)}")
        db.rollback()
        raise CustomException(f"Error creating todo: {str(e)}", sys)
