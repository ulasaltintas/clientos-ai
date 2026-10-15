from sqlalchemy.orm import DeclarativeBase

#sqlalc uses Base to register database models and their table definitions
class Base(DeclarativeBase):
    pass