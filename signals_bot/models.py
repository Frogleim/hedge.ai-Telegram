from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import ENUM  # Use PostgreSQL specific ENUM type

from dotenv import load_dotenv
import os
from sqlalchemy import Enum


# Load environment variables
load_dotenv(dotenv_path=os.path.abspath('.env'))


# Create the database URL
DATABASE_URL='postgresql://virtuum_owner:npg_A2rhO4MTipyW@ep-ancient-dew-a5zf8onm-pooler.us-east-2.aws.neon.tech/virtuum?sslmode=require'
engine = create_engine(DATABASE_URL)

# Define the Base Model
Base = declarative_base()


class PaymentTypeEnum(Enum):
    FREE = "free"
    TONCOIN = "toncoin"
    CRYPTO = "crypto"
    CARD = "card"




class User(Base):
    __tablename__ = 'accounts_telegramuser'  # Matches Django's default table name

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(255), unique=True, nullable=True)
    telegram_username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    trial = Column(Boolean, default=False, nullable=False)
    paid = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<TelegramUser {self.telegram_username}>"



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


if __name__ == "__main__":
    print(User.__table__.columns.keys())