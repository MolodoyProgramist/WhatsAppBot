import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType
)
from aiogram.filters import CommandStart

BOT_API = '7791076321:AAE53gUtBvTJvjIpXdOr-rP5v3Lw6KOkp1k'
ADMIN_ID = 7652762716  # Вставь сюда свой Telegram ID

bot = Bot(token=BOT_API)
dp = Dispatcher()

active_chats = {}

# Главное меню клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Сдать номер")],
        [KeyboardButton(text="💼 Прайс и информация")],
        [KeyboardButton(text="🆘 Поддержка и помощь")],
        [KeyboardButton(text="⏳ Очередь на сдачу")]
    ],
    resize_keyboard=True
)

# Клавиатура с кнопкой "Назад в меню"
back_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад в меню")]],
    resize_keyboard=True
)

# Словарь для хранения состояний пользователей
user_states = {}

# Кнопка завершения чата
anon_chat_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Завершить чат", callback_data="end_chat")]
    ]
)

user_states = {}
waiting_users = []
active_chats = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Добро пожаловать в тиму Lexx Warent | WhatsApp!", reply_markup=main_keyboard)

@dp.message(F.text == "🆘 Поддержка и помощь")
async def support(message: Message):
    text = (
        "✨ Нужна помощь?\n"
        "Свяжитесь с владельцем проекта — всегда готов(а) помочь! 📱\n\n"
        "📩 Telegram: @Lexx_Maboy\n"
    )
    await message.answer(text, reply_markup=main_keyboard)

@dp.message(F.text == "💼 Прайс и информация")
async def price_info(message: Message):
    text = (
        "Привет!\n"
        "Ты в тиме по сдаче ВЦ — здесь ты можешь сдавать свой WhatsApp и получать оплату 💸\n\n"
        "📌 Как это работает:\n"
        "▫️ Ты сдаёшь свой аккаунт (номер/вц/) на время\n"
        "▫️ Другой человек заходит и сидит от твоего имени\n"
        "▫️ Если всё прошло без слёта/палева — ты получаешь деньги\n\n"
        "💬 Никаких вложений. Только доступ, стабильность и немного времени.\n\n"
        "📊 Прайс за ВЦ:\n"
        "🔸 1 ч 15 мин — 11$\n"
        "🔸 2 ч — 15$\n"
        "🔸 3 ч — 19$\n\n"
        "⚠️ Главное — чтобы всё прошло чисто:\n"
        "▪️ Без переписок во время сессии\n"
        "▪️ Без смены устройства/IP\n"
        "▪️ Просто отдал, подождал, получил 💰\n\n"
        "Готов(а) — пиши кураторам, бери слот и начинай зарабатывать уже сегодня."
    )
    await message.answer(text, reply_markup=main_keyboard)

@dp.message(F.text == "⏳ Очередь на сдачу")
async def queue_info(message: Message):
    await message.answer("🎯 Максимальное количество слотов: 200")


@dp.message(F.text == "⬅️ Назад в меню")
async def back_to_menu(message: Message):
    user_states.pop(message.from_user.id, None)  # Сбрасываем состояние
    await message.answer("Вы вернулись в главное меню:", reply_markup=main_keyboard)

@dp.message(F.text == "📱 Сдать номер")
async def ask_number(message: Message):
    user_states[message.from_user.id] = {'awaiting_number': True}
    await message.answer("Отправьте ваш номер в формате +7XXXXXXXXXX", reply_markup=back_keyboard)

@dp.message()
async def handle_number(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state and state.get('awaiting_number'):
        number = message.text.strip()
        if not number.startswith("+7") or len(number) < 11:
            await message.answer(
                "❌ Наша тима принимает только номера из РФ 🇷🇺.\nПожалуйста, попробуйте снова.",
                reply_markup=main_keyboard
            )
            user_states.pop(user_id)
            return

        # Принимаем номер, отправляем админу
        user_states[user_id] = {
            'awaiting_number': False,
            'number': number
        }

        # Кнопка "Отправить код" для админа
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отправить код", callback_data=f"send_code:{user_id}")]
        ])

        await bot.send_message(
            ADMIN_ID,
            f"Поступил номер от пользователя <a href='tg://user?id={user_id}'>id:{user_id}</a>:\n{number}",
            reply_markup=inline_kb,
            parse_mode="HTML"
        )

        await message.answer("✅ Номер принят и отправлен на проверку администратору.", reply_markup=main_keyboard)

        # Отправляем админу с кнопкой начать чат
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔁 Начать анонимный чат", callback_data=f"anon_chat:{user_id}")]
        ])
        await bot.send_message(
            ADMIN_ID,
            f"📥 Новый номер от <a href='tg://user?id={user_id}'>id:{user_id}</a>:\n{number}",
            reply_markup=kb,
            parse_mode="HTML"
        )
        return

        # Пересылка в анонимном чате
    if user_id in active_chats:
        receiver_id = active_chats[user_id]['partner_id']
        await bot.send_message(receiver_id, message.text)
    else:
        await message.answer("❗ Вы не в чате. Нажмите «📱 Сдать номер», чтобы начать.")

    # Если не в состоянии ожидать номер, ничего не делать или можно добавить обработку других сообщений



# Анонимный чат запуск
@dp.callback_query(F.data.startswith("anon_chat:"))
async def start_anon_chat(callback: CallbackQuery):
    admin_id = callback.from_user.id
    user_id = int(callback.data.split(":")[1])

    # Подключение
    active_chats[admin_id] = {'partner_id': user_id}
    active_chats[user_id] = {'partner_id': admin_id}

    await bot.send_message(user_id, "✅ Вы подключены к администратору. Начните диалог.", reply_markup=anon_chat_kb)
    await bot.send_message(admin_id, f"🟢 Вы подключены к пользователю <a href='tg://user?id={user_id}'>id:{user_id}</a>", reply_markup=anon_chat_kb, parse_mode="HTML")
    await callback.answer()

# Завершение чата
@dp.callback_query(F.data == "end_chat")
async def end_chat(callback: CallbackQuery):
    sender_id = callback.from_user.id
    partner_id = active_chats.get(sender_id, {}).get('partner_id')

    if partner_id:
        await bot.send_message(sender_id, "❌ Чат завершён.", reply_markup=main_keyboard)
        await bot.send_message(partner_id, "❌ Администратор завершил чат.", reply_markup=main_keyboard)
        active_chats.pop(sender_id)
        active_chats.pop(partner_id)
    else:
        await bot.send_message(sender_id, "❗ Вы не находитесь в чате.", reply_markup=main_keyboard)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
