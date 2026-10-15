#We want each API request to have its own session so that connections are properly managed
from typing import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]: #Dependency that provides a database session for each request
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()