import asyncio

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config_reader import config
from bot.common import ThrowChoiceCallbackFactory, NFTGiftCallbackFactory
from bot.handlers.common import get_unsubscribed_channels
from bot.db.models import User, NFT
from bot.handlers.common import play
from bot.keyboards import get_inline_keyboard_for_free_step, get_invite_markup
from bot.answer_texts import INVOICE_TEXT, INVITE_TEXT, get_win_text, NO_USERNAME_TEXT


router = Router(name="callbacks-router")


@router.callback_query(ThrowChoiceCallbackFactory.filter())
async def process_main_callback_button(
        query: CallbackQuery,
        callback_data: ThrowChoiceCallbackFactory,
        session: AsyncSession,
        bot: Bot):
    if not query.from_user.username:
        await query.message.answer(NO_USERNAME_TEXT)
        return
    user = await session.get(User, query.from_user.id)
    if callback_data.cost:
        if user.stars_count >= callback_data.cost:
            user.stars_count -= callback_data.cost
            session.add(user)
            await session.commit()
            await play(callback_data.cost, callback_data.throws_count, callback_data.is_premium,
                query.message, user, session, bot)
        else:
            prices = [LabeledPrice(label="XTR", amount=callback_data.cost)]
            await query.message.answer_invoice(
                title='Баскет',
                description=INVOICE_TEXT,
                prices=prices,
                provider_token="",
                payload=f"{callback_data.cost}_stars",
                currency="XTR"
            )
    else:
        if (channel_links := await get_unsubscribed_channels(query.from_user.id, session, bot)):
            await query.message.answer('Подпишитесь на каналы чтобы получить бесплатные броски!',
                reply_markup=get_inline_keyboard_for_free_step(channel_links))
        else:
            await play(0, 6, False, query.message, user, session, bot)


@router.callback_query(F.data == 'check')
async def process_check_button(query: CallbackQuery, session: AsyncSession, bot: Bot):
    user_id = query.from_user.id
    user = await session.get(User, user_id)
    channel_ids = user.channel_ids_to_subscribe.split()
    for channel_id in channel_ids:
        is_member = False
        try:
            member_answer = await bot.get_chat_member(channel_id, user_id)
            is_member = member_answer and \
                member_answer.status.lower() not in ('left', 'restricted', 'kicked')
        except:
            ...
        if not is_member:
            await query.message.answer('Вы не подписались на все каналы') ##TODO проверить как в ориг боте
            return
    await play(0, 6, False, query.message, user, session, bot)


@router.callback_query(F.data == 'invite')
async def process_invite_button(query: CallbackQuery):
    await query.message.answer(INVITE_TEXT, reply_markup=get_invite_markup(query.from_user.id))


@router.callback_query(F.data == 'no_free_left')
async def process_no_free(query: CallbackQuery, session: AsyncSession, bot: Bot):
    if query.from_user.id != config.second_admin_id:
        return
    user = await session.get(User, query.from_user.id)
    await play(0, 6, False, query.message, user, session, bot)


@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(
    message: Message,
    session: AsyncSession,
    bot: Bot
):
    amount = message.successful_payment.total_amount
    user = await session.get(User, message.from_user.id)
    if amount == 1:
        await play(1, 5, False,
                message, user, session, bot)
    if amount == 5:
        await play(5, 3, False,
                message, user, session, bot)
    if amount == 8:
        await play(8, 2, False,
                message, user, session, bot)
    if amount == 10:
        await play(10, 1, False,
                message, user, session, bot)
    if amount == 15:
        await play(15, 1, False,
                message, user, session, bot)
    if amount >= 20:
        await message.answer("Спасибо, платеж принят")


@router.callback_query(NFTGiftCallbackFactory.filter())
async def process_main_callback_button(
        query: CallbackQuery,
        callback_data: NFTGiftCallbackFactory,
        session: AsyncSession,
        bot: Bot):
    nft = await session.get(NFT, callback_data.nft_id)

    if nft.owner_id:
        await query.message.answer('Подарок уже был отправлен ранее')
        return

    user = await session.get(User, callback_data.user_id)
    msg = get_win_text(user, nft)
    nft.owner_id = user.user_id
    session.add(nft)
    await session.commit()
    await bot.send_message(config.channel_id, msg)
