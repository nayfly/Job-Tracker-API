import os

# ensure testing environment is set before any application code is imported
os.environ.setdefault("ENV", "test")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db import session as db_session
from app.db.base import Base


def _create_test_engine():
    url = settings.database_url
    # when using sqlite:///:memory: we want a single shared connection
    # so that create_all() and subsequent sessions see the same schema.
    if url == "sqlite:///:memory:":
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    # otherwise just create normally (e.g. file sqlite or postgres)
    kwargs = {}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **kwargs)


@pytest.fixture(autouse=True, scope="session")
def configure_environment():
    # make sure testing env is set before settings are evaluated elsewhere
    os.environ.setdefault("ENV", "test")
    # force reload of settings object in case it was created earlier
    # importlib.reload(settings.__class__)
    yield


@pytest.fixture(autouse=True)
def prepare_database(tmp_path, monkeypatch):
    # override the module-level engine and SessionLocal used by application
    test_engine = _create_test_engine()
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine, expire_on_commit=False)

    monkeypatch.setattr(db_session, "engine", test_engine)
    monkeypatch.setattr(db_session, "SessionLocal", TestSession)
    # update any imported references (e.g. deps.get_db) so they use the
    # patched SessionLocal as well
    import app.core.deps as deps_module
    monkeypatch.setattr(deps_module, "SessionLocal", TestSession)

    # create tables
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)
