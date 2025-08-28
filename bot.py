import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # from Render Environment Variables
ADMIN_ID = os.getenv("ADMIN_ID")  # your telegram user id

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_data = {}

# Step 1 - Start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.chat.id] = {}
    await message.answer("👋 Welcome! Let's get started.\nPlease enter your *Full Name*:")

# Step 2 - Name
@dp.message_handler(lambda message: message.chat.id in user_data and "name" not in user_data[message.chat.id])
async def get_name(message: types.Message):
    user_data[message.chat.id]["name"] = message.text
    await message.answer("📅 Enter your Date of Birth (YYYY-MM-DD):")

# Step 3 - DOB
@dp.message_handler(lambda message: message.chat.id in user_data and "dob" not in user_data[message.chat.id])
async def get_dob(message: types.Message):
    dob = message.text
    if len(dob.split("-")) != 3:
        await message.answer("❌ Invalid format. Please use YYYY-MM-DD:")
        return
    user_data[message.chat.id]["dob"] = dob
    await message.answer("🏫 Enter your High School name:")

# Step 4 - High School
@dp.message_handler(lambda message: message.chat.id in user_data and "school" not in user_data[message.chat.id])
async def get_school(message: types.Message):
    user_data[message.chat.id]["school"] = message.text
    await message.answer("🏠 Enter your Address line 1:")

# Step 5 - Address
@dp.message_handler(lambda message: message.chat.id in user_data and "address" not in user_data[message.chat.id])
async def get_address(message: types.Message):
    user_data[message.chat.id]["address"] = message.text
    await message.answer("📸 Now send your Photo:")

# Step 6 - Photo
@dp.message_handler(content_types=["photo"])
async def get_photo(message: types.Message):
    if "photo" not in user_data[message.chat.id]:
        user_data[message.chat.id]["photo"] = message.photo[-1].file_id

        summary = (
            f"✅ Please confirm your details:\n\n"
            f"👤 Name: {user_data[message.chat.id]['name']}\n"
            f"📅 DOB: {user_data[message.chat.id]['dob']}\n"
            f"🏫 School: {user_data[message.chat.id]['school']}\n"
            f"🏠 Address: {user_data[message.chat.id]['address']}\n\n"
            f"Is this correct?"
        )

        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("✅ Yes"), KeyboardButton("❌ No"))

        await message.answer(summary, reply_markup=keyboard)

# Step 7 - Confirmation
@dp.message_handler(lambda message: message.text in ["✅ Yes", "❌ No"])
async def confirm(message: types.Message):
    if message.text == "✅ Yes":
        data = user_data[message.chat.id]
        await bot.send_message(ADMIN_ID, f"🎉 New Submission:\n\n"
                                         f"👤 Name: {data['name']}\n"
                                         f"📅 DOB: {data['dob']}\n"
                                         f"🏫 School: {data['school']}\n"
                                         f"🏠 Address: {data['address']}")
        await bot.send_photo(ADMIN_ID, data["photo"])
        await message.answer("🎉 Thank you! Your information has been submitted.")
        del user_data[message.chat.id]
    else:
        user_data[message.chat.id] = {}
        await message.answer("❌ Let's try again. Please enter your *Full Name*:")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
