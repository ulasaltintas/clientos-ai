#conftest.py is a special pytest file used to define reusable test fixtures.


import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.main import app


# Use the same PostgreSQL server, but a separate database.
DEV_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://clientos:clientos_dev_password@127.0.0.1:5432/clientos_db",
)

dev_url = make_url(DEV_DATABASE_URL)

if dev_url.database != "clientos_db":
    raise RuntimeError("Unexpected development database configuration")

TEST_DATABASE_URL = dev_url.set(
    database="clientos_test_db"
)

if TEST_DATABASE_URL.database != "clientos_test_db":
    raise RuntimeError("Tests must use clientos_test_db")



test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
)



@pytest.fixture #sets up a reusable test environment
def client():
    # Open a dedicated database connection
    connection = test_engine.connect()

    # Start an outer transaction
    transaction = connection.begin()

    def override_get_db():
        with Session(
            bind=connection,
            join_transaction_mode="create_savepoint", #this allows the API endpoints to call db.commit() without affecting the outer transaction
        ) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db #tells FastAPI to use override_get_db function whenever an endpoint asks for the database dependency during the test

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

        # Undo all database changes from this test
        transaction.rollback()
        connection.close()

