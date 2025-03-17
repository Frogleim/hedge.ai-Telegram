from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM  # Use PostgreSQL specific ENUM type

from dotenv import load_dotenv
import os
from sqlalchemy import Enum


# Load environment variables
load_dotenv(dotenv_path=os.path.abspath('.env'))

# Database credentials
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")  # For Docker container
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "hedge.ai")

# Create the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

# Define the Base Model
Base = declarative_base()


class PaymentTypeEnum(Enum):
    FREE = "free"
    TONCOIN = "toncoin"
    CRYPTO = "crypto"
    CARD = "card"



class User(Base):
    """User table for managing subscriptions"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False)
    status = Column(String, default="trial")  # trial, active, expired
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)  # Defaults to now, modify after trial
    expiry_date = Column(DateTime, nullable=True)  # For paid subscription expiry
    payment_type = Column(String, default=None,  nullable=True)

class Wallets(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, nullable=False)
    wallet_network = Column(String, nullable=True)

# Create Tables
Base.metadata.create_all(engine)

# Create a session
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session():
    """Returns a new database session"""
    return SessionLocal()