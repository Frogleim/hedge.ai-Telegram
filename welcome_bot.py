import logging
import os
import asyncio
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
            # InlineKeyboardButton(text="By Card", callback_data="pay_card"),
            InlineKeyboardButton(text="By Crypto", callback_data="pay_crypto")
        ]
    ])

def crypto_selection_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Pay Now 💳", url="http://127.0.0.1:8000/payment/process/")
        ]

    ])


from aiogram import types
from aiogram.filters import Command


@dp.message(Command("start"))
async def start(message: types.Message):
    db = db_utils.DB()
    user_id = message.from_user.id
    username = message.from_user.username

    print(user_id)
    print(username)

    user_data = {
        "telegram_id": user_id,
        "telegram_username": username,
        "status": "pending",
        "payment_type": "not paid",
    }

    is_not_exist = db.add_new_user(user_data)
    if is_not_exist:
        welcome_text = """
        🎉 <b>Welcome to the Hedge.ai!</b> 🚀

        Welcome to the ultimate <b>Trading Signals</b> bot designed to help you make smarter trading decisions with ease! Whether you're a beginner or an experienced trader, our service provides you with <b>real-time, reliable trade signals</b> to enhance your trading strategies.

        ---

        <b>What We Offer:</b>
        - ⚡ <b>Accurate Signals:</b> Get trade signals with clear entry and exit points.
        - 💡 <b>Market Insights:</b> Stay updated on market trends and conditions.
        - 📈 <b>Performance Tracking:</b> Monitor your trades and their performance over time.
        - 🚀 <b>Expert Recommendations:</b> Tailored suggestions based on thorough market analysis.

        ---

        <b>Start Your Journey:</b>
        - 💥 <b>Free 7-Day Trial:</b> Try our service for 7 days at no cost and experience the quality of our signals firsthand!
        - 💳 <b>Subscribe to Unlock Full Access:</b> If you love the service, upgrade to a paid plan for uninterrupted access to premium signals.

        ---

        <b>Payment Methods:</b>
        We offer multiple payment options, including <b>credit card</b> and <b>cryptocurrencies</b> like <b>Bitcoin, Ethereum (ERC20), Solana</b>, and <b>TRC20</b>.

        Ready to make your next move in the market? Start your trial or subscribe now and take your trading to the next level! 🚀
        """

        await message.answer(
            welcome_text,
            parse_mode="HTML",  # ✅ Use HTML (No need to escape characters)
            reply_markup=start_trial_keyboard()
        )
    else:
        await message.answer(
            "Welcome back! For getting signals, please open this Telegram bot: [t.me/hedge_ai_crypto11_bot](https://t.me/hedge_ai_crypto11_bot)",
            parse_mode="Markdown",  # ✅ Use Markdown for links
        )
# Handle Start Trial Button
@dp.callback_query(lambda c: c.data == "start_trial")
async def on_start_trial(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    db = db_utils.DB()

    db.change_user_status(user_id, 'trial')

    await callback_query.message.edit_text("🎉 You are now on a 7-day free trial for trade signals! [t.me/hedge_ai_crypto11_bot](https://t.me/hedge_ai_crypto11_bot)", parse_mode="Markdown")


# Handle Subscription Button -> Ask for Payment Method
@dp.callback_query(lambda c: c.data == "subscribe")
async def choose_payment_method(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    db = db_utils.DB()

    db.change_user_status(user_id, 'pending')

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
        "🔹 Click the button below to proceed with the crypto payment:",
        reply_markup=crypto_selection_keyboard()
    )




async def on_start():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(on_start())