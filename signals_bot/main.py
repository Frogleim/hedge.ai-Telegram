import json
import logging
import asyncio
import aio_pika
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
import db_utils
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_MONITORING")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")
QUEUE_NAME = os.getenv("QUEUE_NAME")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()




@dp.message(Command('start'))
async def start_command(message: types.Message):
    """Handle the /start command."""

    db = db_utils.DB()
    username = message.from_user.username
    telegram_id = message.from_user.id
    print(telegram_id)
    db.update_user_data(username, telegram_id)
    is_allowed = db.check_user(username)
    if not is_allowed:
        await message.answer('You are not allowed to get trading signal. Please subscribe or get 7 days trial.\n https://virtuum.xyz', parse_mode='MARKDOWN')
    else:
        await message.answer("👋 Welcome! This bot will send you trade signals. Stay tuned!")


async def send_telegram_message(trade_signal):
    """Send trade signal to Telegram chat."""
    try:
        # Create the message content
        message = (
            f"📢 *Trade Signal Received!*\n\n"
            f"📍 *Symbol:* {trade_signal.get('symbol', 'N/A')}\n"
            f"📈 *Entry Price:* {trade_signal.get('entry_price', 'N/A')}\n"
            f"📊 *Long EMA:* {trade_signal.get('long_ema', 'N/A')}\n"
            f"📉 *Short EMA:* {trade_signal.get('short_ema', 'N/A')}\n"
            f"⚡ *ADX:* {trade_signal.get('adx', 'N/A')}\n"
            f"📊 *RSI:* {trade_signal.get('rsi', 'N/A')}\n"
            f"🎯 *ATR:* {trade_signal.get('atr', 'N/A')}\n"
            f"📢 *Volume:* {trade_signal.get('volume', 'N/A')}\n"
            f"🛠 *Trade Side:* {trade_signal.get('side', 'N/A')}\n"
        )

        db = db_utils.DB()
        all_users = db.get_all_active_users()
        send_messages = [
            bot.send_message(chat_id=user, text=message, parse_mode=ParseMode.MARKDOWN)
            for user in all_users
        ]

        await asyncio.gather(*send_messages)

        logger.info(f"✅ Trade signal sent to Telegram: {trade_signal.get('symbol')}")

    except Exception as e:
        logger.error(f"❌ Error sending trade signal to Telegram: {e}")




async def process_message(queue):

    """Continuously process messages from the queue."""

    while True:
        trade_signal = await queue.get()
        await send_telegram_message(trade_signal)


async def consume_rabbitmq():

    """Listen for messages from RabbitMQ asynchronously."""

    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
    )
    queue = asyncio.Queue()

    async def on_message(message: aio_pika.IncomingMessage):
        """Process received messages."""
        async with message.process():
            trade_signal = json.loads(message.body.decode('utf-8'))
            logger.info(f"📩 Trade Signal Received: {trade_signal}")
            await queue.put(trade_signal)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue_obj = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue_obj.consume(on_message)

    logger.info("📡 Listening for trade signals from RabbitMQ...")

    await process_message(queue)


async def main():
    """Start the bot and RabbitMQ consumer concurrently."""
    await asyncio.gather(
        consume_rabbitmq(),
        dp.start_polling(bot)
    )


if __name__ == "__main__":
    from multiprocessing import Process

    Process(target=main).start()
    asyncio.run(main())