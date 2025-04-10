import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User  # Assuming this is where your SQLAlchemy model is defined
from dotenv import load_dotenv
from aiogram import Bot
from . import loggs_handler
import asyncio

load_dotenv()

# Setup your database connection
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_MONITORING")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_message(chat_id, message):

    """Send message to a user via Telegram"""

    await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")


def check_if_expired():
    session = Session()
    try:
        current_timestamp = datetime.now().timestamp()
        expired_users = []

        users = session.query(User).all()
        for user in users:
            expiry_timestamp = user.expiry_date.timestamp() if user.expiry_date else float('inf')
            trial_timestamp = user.trial_end.timestamp() if user.trial_end else float('inf')

            if expiry_timestamp < current_timestamp or trial_timestamp < current_timestamp:
                if user.status != "expired":
                    user.status = "expired"
                    session.commit()
                    loggs_handler.system_log.info(f'User {user.telegram_username} has expired')
                    expired_users.append(user.telegram_id)

    except Exception as e:
        session.rollback()
        loggs_handler.system_log.error(f"Database error: {e}")

    finally:
        session.close()  # Ensure session is always closed


async def send_expiry_messages(users):
    for user_id in users:
        await send_telegram_message(user_id, "⚠️ Your subscription has expired. Please renew to continue receiving trade signals.")


if __name__ == "__main__":
    import schedule
    import time


    while True:
        check_if_expired()
        time.sleep(60)