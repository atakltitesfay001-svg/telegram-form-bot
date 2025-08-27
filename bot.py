from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
import re

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
ADMIN_ID = YOUR_TELEGRAM_ID_HERE  # Replace with your ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Step-by-step states
class Form(StatesGroup):
    name = State()
    dob = State()
    school = State()
    address = State()
    photo = State()
    confirm = State()

# Start
@dp.message_handler(commands=['start'])
async def start_form(message: types.Message):
    await message.answer("👋 Hello! Let's get started.\nWhat is your full name?")
    await Form.name.set()

# Name
@dp.message_handler(state=Form.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📅 Enter your date of birth (YYYY-MM-DD):")
    await Form.dob.set()

# DOB Validation
@dp.message_handler(state=Form.dob)
async def get_dob(message: types.Message, state: FSMContext):
    dob = message.text.strip()
    if not re.match(r"\d{4}-\d{2}-\d{2}", dob):
        await message.answer("❌ Invalid date format. Please enter in YYYY-MM-DD.")
        return
    await state.update_data(dob=dob)
    await message.answer("🏫 What's your high school name?")
    await Form.school.set()

# School
@dp.message_handler(state=Form.school)
async def get_school(message: types.Message, state: FSMContext):
    await state.update_data(school=message.text)
    await message.answer("📍 Enter your address (line 1 only):")
    await Form.address.set()

# Address
@dp.message_handler(state=Form.address)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("🖼️ Please send a photo of yourself:")
    await Form.photo.set()

# Photo
@dp.message_handler(content_types=['photo'], state=Form.photo)
async def get_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)

    data = await state.get_data()
    summary = (
        f"📝 **Please Confirm Your Info:**\n\n"
        f"👤 Name: {data['name']}\n"
        f"📅 DOB: {data['dob']}\n"
        f"🏫 School: {data['school']}\n"
        f"📍 Address: {data['address']}\n\n"
        f"Is this correct? ✅ Yes / ❌ No"
    )
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Yes"), KeyboardButton("❌ No"))
    await message.answer(summary, reply_markup=markup, parse_mode="Markdown")
    await Form.confirm.set()

# Confirm or Correct
@dp.message_handler(state=Form.confirm)
async def confirm_data(message: types.Message, state: FSMContext):
    if message.text == "✅ Yes":
        data = await state.get_data()
        await bot.send_message(ADMIN_ID, f"📬 New Submission:\n\n"
                                          f"👤 Name: {data['name']}\n"
                                          f"📅 DOB: {data['dob']}\n"
                                          f"🏫 School: {data['school']}\n"
                                          f"📍 Address: {data['address']}")
        await bot.send_photo(ADMIN_ID, data['photo'])

        await message.answer("🎉 Thank you! Your information has been submitted.")
        await state.finish()
    elif message.text == "❌ No":
        await message.answer("📝 Which part do you want to correct? (Name, DOB, School, Address)")
        # Optional: implement specific correction logic
        await state.finish()
    else:
        await message.answer("Please reply with ✅ Yes or ❌ No")

# Run bot
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
