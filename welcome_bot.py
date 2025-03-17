import logging
import os
import asyncio
import qrcode  # QR code library
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from core import db_utils

# Load environment variables
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Set up logging
logging.basicConfig(level=logging.INFO)


# Inline Keyboards
def start_trial_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Start Trial", callback_data="start_trial"),
            InlineKeyboardButton(text="Subscribe", callback_data="subscribe")
        ]
    ])

def payment_method_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="By Card", callback_data="pay_card"),
            InlineKeyboardButton(text="By Crypto", callback_data="pay_crypto")
        ]
    ])

def crypto_selection_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="TRC20", callback_data="crypto_TRC20"),
            InlineKeyboardButton(text="ERC20", callback_data="crypto_ERC20")
        ],
        [
            InlineKeyboardButton(text="Solana", callback_data="crypto_Solana"),
            InlineKeyboardButton(text="Bitcoin", callback_data="crypto_Bitcoin")
        ]
    ])


# Command handler for '/start'
@dp.message(Command("start"))
async def start(message: types.Message):
    db = db_utils.DB()

    user_id = message.from_user.id
    user_data = {
        "user_id": user_id,
        "status": "trial",
        "payment_type": 'not paid',
    }

    db.add_new_user(user_data)

    await message.answer(
        "🎉 Welcome! Choose an option:\n"
        "You have a 7-day free trial for trade signals, or you can subscribe directly.",
        reply_markup=start_trial_keyboard()
    )


# Handle Start Trial Button
@dp.callback_query(lambda c: c.data == "start_trial")
async def on_start_trial(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    db = db_utils.DB()

    db.change_user_status(user_id, 'trial')

    await callback_query.message.edit_text("🎉 You are now on a 7-day free trial for trade signals!")


# Handle Subscription Button -> Ask for Payment Method
@dp.callback_query(lambda c: c.data == "subscribe")
async def choose_payment_method(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "💳 Please select a payment method:",
        reply_markup=payment_method_keyboard()
    )


# Handle Payment by Card
@dp.callback_query(lambda c: c.data == "pay_card")
async def pay_by_card(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    db = db_utils.DB()

    db.change_user_status(user_id, 'active')
    db.update_payment_method(user_id, 'card')

    await callback_query.message.edit_text("✅ Payment successful! You are now subscribed via Card.")


# Handle Payment by Crypto -> Ask for Cryptocurrency
@dp.callback_query(lambda c: c.data == "pay_crypto")
async def select_crypto(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "🔹 Choose your preferred cryptocurrency:",
        reply_markup=crypto_selection_keyboard()
    )


# Handle Selected Cryptocurrency -> Fetch & Display Wallet QR Code
@dp.callback_query(lambda c: c.data.startswith("crypto_"))
async def pay_by_selected_crypto(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    db = db_utils.DB()

    # Extract cryptocurrency type from callback data
    selected_crypto = callback_query.data.split("_")[1]  # e.g., "crypto_TRC20" → "TRC20"

    # Fetch the correct wallet address from the database
    wallet_address = db.get_wallet_address(selected_crypto)  # Implement this function in db_utils

    if not wallet_address:
        await callback_query.message.edit_text(f"❌ No wallet address found for {selected_crypto}.")
        return

    # Generate QR code
    qr_code_path = f"wallet_qr_{selected_crypto}.png"
    generate_qr_code(wallet_address, qr_code_path)

    # Update database with user payment choice
    db.change_user_status(user_id, 'active')
    db.update_payment_method(user_id, selected_crypto)

    # Send QR Code & Wallet Address
    qr_code = FSInputFile(qr_code_path)
    await callback_query.message.answer_photo(
        qr_code, caption=f"📌 Scan this QR code to pay with **{selected_crypto}**.\n\n"
                         f"💰 Wallet Address: `{wallet_address}`\n\n"
                         f"Subscription price: 15 USDT/month"
    )


# Generate QR Code for a given address
def generate_qr_code(wallet_address, file_path):
    qr = qrcode.make(wallet_address)
    qr.save(file_path)


# Main entry point for the bot
async def on_start():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(on_start())