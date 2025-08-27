import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from dotenv import load_dotenv


load_dotenv()


bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher()

CHANNEL_ID = '-1002973485938' # id тестового канала (в будущем будут динамически обновляться)


def get_main_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='🆓🏀 6 мячей бесплатно', callback_data='make_6'))
    builder.row(InlineKeyboardButton(text='🏀 5 мячей · 1 ⭐', callback_data='make_5'),
                 InlineKeyboardButton(text='🏀 3 мяча · 5 ⭐', callback_data='make_3'))
    builder.row(InlineKeyboardButton(text='🏀 2 мяча · 8 ⭐', callback_data='make_2'),
                 InlineKeyboardButton(text='🏀 1 мяч · 10 ⭐', callback_data='make_1'))
    return builder.as_markup()


def get_inline_keyboard_for_free_step():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Подписаться', url='https://t.me/msk_afisha_20'))
    builder.row(InlineKeyboardButton(text='Проверить', callback_data='check_subs'))
    return builder.as_markup()


answer_text = '''🏀 Попади каждым броском в кольцо и получи крутой [подарок, подробнее.](https://telegra.ph/Poluchaj-Telegram---podarki-za-kazhduyu-pobedu-08-20)

🏆 Выпал кубок - приз NFT подарок.'''


@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    await main_answer(message)

async def main_answer(message: types.Message):
    await message.answer(answer_text, reply_markup=get_main_inline_keyboard(), parse_mode='markdown', disable_web_page_preview=True)

@dp.callback_query(lambda c: c.data and c.data.startswith('make'))
async def process_callback_button(callback_query: types.CallbackQuery):
    choice = callback_query.data.split('_')[-1]
    print(choice)
    if choice == '6':
        await callback_query.message.answer('Подпишитесь на каналы чтобы получить бесплатные броски!', reply_markup=get_inline_keyboard_for_free_step())
    else:
        await roll_dice(callback_query.message, int(choice))
    await callback_query.answer() # Always answer the callback query


@dp.callback_query(lambda c: c.data and c.data.startswith('check'))
async def process_free_request(callback_query: types.CallbackQuery):
    try:
        mem = await bot.get_chat_member(CHANNEL_ID, callback_query.from_user.id)
        if mem.status.lower() not in ('left', 'restricted', 'kicked'):
            await roll_dice(callback_query.message)
        else:
            raise
    except:
        await callback_query.message.answer('Вы не подписались на все каналы')
    await callback_query.answer()


async def roll_dice(message: types.Message, n: int = 6):
    if n < 6:
        await message.answer('[здесь будет покупка за звезды]')
        await asyncio.sleep(0.6)
    data = []
    for i in range(n):
        res = await bot.send_dice(message.chat.id, emoji='🏀')
        await asyncio.sleep(0.5)
        data.append(res.dice.value)
    await asyncio.sleep(0.3 * i)
    answer_text = '**Результат игры**'
    for d in data:
        answer_text += '\n**❌Промах**' if d < 4 else '\n**✅Попал**'
    await bot.send_message(message.chat.id, answer_text, parse_mode='markdown')
    await asyncio.sleep(0.7)
    if all(d > 3 for d in data):
        await bot.send_message(message.chat.id, '🎉')
        await bot.send_message(message.chat.id, '[здесь будет отправка подарка и инфо о нем]')
    else:
        await bot.send_message(message.chat.id, 'В следующий раз обязательно повезет! Сыграем еще раз?')
    await asyncio.sleep(0.7)
    await main_answer(message)



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())