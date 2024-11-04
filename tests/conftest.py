import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from currency_app.api.main import app
from currency_app.db import Base
from currency_app.settings import settings


@pytest.fixture(autouse=True)
def db_init(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(settings.database_dsn.get_secret_value())
    assert engine is not None
    return engine


@pytest.fixture
def db_session(engine):
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        sess = local_session()
        try:
            yield sess
        finally:
            sess.close()

    return get_db


@pytest.fixture()
def db_api(db_session):
    s = db_session()
    yield next(s)
    s.close()
