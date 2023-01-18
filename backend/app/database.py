import sqlalchemy as _sql
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm
from app.config import Configs

DATABASE_URL = Configs.DATABASE_URL

engine = _sql.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _declarative.declarative_base()
