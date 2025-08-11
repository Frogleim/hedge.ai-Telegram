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
import loggs_handler

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_MONITORING")

QUEUE_NAME = os.getenv("QUEUE_NAME", "trade_signals")

# Directly use the RabbitMQ URL you provided
RABBIT_URL = "amqp://guest:guest@ec2-13-37-216-56.eu-west-3.compute.amazonaws.com:5672/"

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
    db.update_user_data(username, telegram_id)
    is_allowed = db.check_user(username)

    if not is_allowed:
        await message.answer(
            'You are not allowed to get trading signals. '
            'Please subscribe or get a 7-day trial.\n https://virtuum.xyz',
            parse_mode='MARKDOWN'
        )
    else:
        await message.answer("👋 Welcome! This bot will send you trade signals. Stay tuned!")


async def send_telegram_message(trade_signal):
    """Send trade signal to all active Telegram users."""
    try:
        message = (
            f"📢 *Trade Signal Received!*\n\n"
            f"📍 *Symbol:* {trade_signal.get('symbol', 'N/A')}\n"
            f"📈 *Entry Price:* {trade_signal.get('price', 'N/A')}\n"
            f"🎯 *TP:* {trade_signal.get('take_profit', 'N/A')}\n"
            f"🛑 *SL:* {trade_signal.get('stop_loss', 'N/A')}\n"
            f"🛠 *Trade Side:* {trade_signal.get('signal', 'N/A')}\n"
            f"⏱ *Time:* {trade_signal.get('timestamp', 'N/A')}"
        )

        db = db_utils.DB()
        all_users = db.get_all_active_users()
        loggs_handler.system_log.info("Sending trade signal to all active Telegram users: {}".format(all_users))
        await asyncio.gather(*[
            bot.send_message(chat_id=user, text=message, parse_mode=ParseMode.MARKDOWN)
            for user in all_users
        ])

        logger.info(f"✅ Trade signal sent to Telegram: {trade_signal.get('symbol')}")
    except Exception as e:
        logger.error(f"❌ Error sending trade signal to Telegram: {e}")


async def consume_rabbitmq():
    """Listen for messages from RabbitMQ asynchronously."""
    connection = await aio_pika.connect_robust(RABBIT_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    async with queue.iterator() as queue_iter:
        loggs_handler.system_log.info(f"📡 Listening for trade signals from RabbitMQ queue {QUEUE_NAME}")
        async for message in queue_iter:
            async with message.process():
                try:
                    trade_signal = json.loads(message.body.decode('utf-8'))
                    loggs_handler.system_log.info(f"📩 Trade Signal Received: {trade_signal}")
                    await send_telegram_message(trade_signal)
                except Exception as e:
                    loggs_handler.system_log.error(f"❌ Failed to process message: {e}")


async def main():
    """Run bot and RabbitMQ consumer together."""
    await asyncio.gather(
        dp.start_polling(bot),
        consume_rabbitmq()
    )


if __name__ == "__main__":
    asyncio.run(main())