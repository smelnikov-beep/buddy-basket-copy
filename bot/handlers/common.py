from datetime import datetime, timezone, timedelta
import asyncio
import random

from aiogram import Bot
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.answer_texts import get_main_answer_text
from bot.keyboards import get_main_inline_keyboard, get_nft_gift_markup
from bot.db.models import User, Channel, NFT
from bot.answer_texts import GET_REFERER_STARS_TEXT
from bot.config_reader import config


async def main_answer(message: Message, user: User, session: AsyncSession):
    free_throws = await update_free_throws(user, session)

    await message.answer(
        get_main_answer_text(user.stars_count),
        reply_markup=get_main_inline_keyboard(free_throws),
        disable_web_page_preview=True)


async def get_unsubscribed_channels(user_id: int, session: AsyncSession, bot: Bot) -> list[str]:
    unsubscribed_links = []
    unsubscribed_ids = ''
    stmt = select(Channel).where(Channel.is_active == True)
    result = await session.execute(stmt)
    channels = result.scalars().all()
    for channel in channels:
        is_member = False
        try:
            membership = await bot.get_chat_member(channel.channel_id, user_id)
            is_member = membership.status.lower() not in ('left', 'restricted', 'kicked')
        except:
            ...
        if not is_member:
            unsubscribed_links.append(channel.link)
            unsubscribed_ids += f'{channel.channel_id},'
        if len(unsubscribed_links) >= 4:
            break
    unsubscribed_ids = unsubscribed_ids.strip(',')
    if unsubscribed_ids:
        user = await session.get(User, user_id)
        user.channel_ids_to_subscribe = unsubscribed_ids
        session.add(user)
        await session.commit()
    return unsubscribed_links


async def play(cost: int, throws_count: int, is_premium: bool,
               message: Message, user: User,
               session: AsyncSession, bot: Bot):
    user.games_count += 1
    if user.games_count == 3 and user.referer_id:
        await send_stars_to_referer(user.referer_id, session, bot)
    if not cost:
        today_msk = (datetime.now(timezone.utc) + timedelta(hours=3)).date()
        user.free_throws -= 1
        user.last_free_throw_date = today_msk
    session.add(user)
    await session.commit()
    data = []
    for i in range(throws_count):
        res = await bot.send_dice(user.user_id, emoji='🏀')
        await asyncio.sleep(0.7)
        data.append(res.dice.value)
    await asyncio.sleep(0.5 * i)
    answer_text = f'<b>Результат игры</b>'
    for d in data:
        answer_text += '\n<b>❌Промах</b>' if d < 4 else '\n<b>✅Попал</b>'
    answer_text += f'\n\n<b>🎁 NFT подарки выпадают только подписчикам канала</b> @{config.channel_link.split("/")[-1]}'
    has_won = all(d > 3 for d in data) or user.user_id in (config.main_admin_id, config.second_admin_id)
    if not has_won:
        answer_text += '\n\nВ следующий раз обязательно повезет! Сыграем еще раз?'
    await bot.send_message(user.user_id, answer_text)
    await asyncio.sleep(0.7)
    if has_won:
        await asyncio.sleep(0.3)
        await bot.send_message(user.user_id, '🎉')
        await asyncio.sleep(0.3)
        await send_gift(message, user, session, bot, is_premium)
    await asyncio.sleep(0.7)
    await main_answer(message, user, session)


async def update_free_throws(user: User, session: AsyncSession) -> int:
    today_msk = (datetime.now(timezone.utc) + timedelta(hours=3)).date()
    if user.last_free_throw_date != today_msk:
        user.free_throws = 4
        session.add(user)
        await session.commit()
    return user.free_throws


async def send_stars_to_referer(referer_id: int, session: AsyncSession, bot: Bot):
    referer = await session.get(User, referer_id)
    referer.stars_count += 3
    msg = await bot.send_message(referer_id, GET_REFERER_STARS_TEXT)
    await main_answer(msg, referer, session)


async def send_gift(message: Message, user: User, session: AsyncSession, bot: Bot, is_premium: bool):
    result = random.randint(0, 100)
    gift_ids = (config.regular_gift_1_id, config.regular_gift_2_id) if not is_premium \
        else (config.premium_gift_1_id, config.premium_gift_2_id)
    gift_id = config.super_gift_id if (result == 50 or user.user_id in (config.main_admin_id, config.second_admin_id)) \
        and (nft := await get_available_nft(session)) else gift_ids[result < 50]
    if user.user_id not in (config.main_admin_id, config.second_admin_id):
        await bot.send_gift(str(gift_id), user.user_id)
    if gift_id == config.super_gift_id:
        await message.answer("Поздравляем, вы выиграли NFT-подарок! В течение суток он будет отправлен нашим админом")
        await send_nft_message_to_admins(nft, user, session, bot)


async def get_available_nft(session: AsyncSession) -> NFT | None:
    stmt = select(NFT).where(NFT.owner_id == 0)
    result = await session.scalars(stmt)
    return result.first()


async def send_nft_message_to_admins(nft: NFT, winner: User, session: AsyncSession, bot: Bot):
    chat = await bot.get_chat(winner.user_id)
    winner.username = chat.username
    winner.name = chat.full_name
    session.add(winner)
    await session.commit()

    message = f"Юзер @{winner.username} выиграл NFT {nft.link}. После отправки нажмите кнопку"
    await bot.send_message(config.main_admin_id, message, reply_markup=get_nft_gift_markup(nft.id, winner.user_id))
    await bot.send_message(config.second_admin_id, message, reply_markup=get_nft_gift_markup(nft.id, winner.user_id))