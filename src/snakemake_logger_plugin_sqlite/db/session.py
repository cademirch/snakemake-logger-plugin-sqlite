from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import os


class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            os.makedirs(os.path.join(".snakemake", "log"), exist_ok=True)
            db_path = os.path.join(".snakemake", "log", "snakemake.log.db")

        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self) -> Session:
        return self.SessionLocal()
