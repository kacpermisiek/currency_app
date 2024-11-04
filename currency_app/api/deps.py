from typing import Iterator

from sqlalchemy.orm import Session

from currency_app.db import get_session
from currency_app.settings import settings


def get_db() -> Iterator[Session]:
    db = get_session(settings.database_dsn)
    try:
        yield db
    finally:
        db.close()
