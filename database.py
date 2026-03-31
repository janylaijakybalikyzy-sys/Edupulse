from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Базанын атын v3 кылдык, бул Render-деги эски каталарды тазалоого жардам берет
SQLALCHEMY_DATABASE_URL = "sqlite:///./edupulse_v3.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()