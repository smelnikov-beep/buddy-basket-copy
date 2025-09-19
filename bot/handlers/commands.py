from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, LabeledPrice
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.common import main_answer
from bot.db.models import User, Channel, NFT
from bot.config_reader import config


router = Router(name="commands-router")


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, session: AsyncSession):
    user = await session.get(User, message.from_user.id)

    args = command.args

    if not user:
        user = User(user_id=message.from_user.id)
        user.name = message.from_user.full_name
        user.username = message.from_user.username or ''
        if args:
            user.referer_id = int(args)
        if message.from_user.id in (config.main_admin_id, config.second_admin_id):
            user.is_admin = True
        session.add(user)
        await session.commit()

    await main_answer(message, user, session)


@router.message(Command("chan"))
async def cmd_chan(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    user = await session.get(User, message.from_user.id)

    if not user.is_admin:
        await message.answer("Только админ может добавлять/смотреть каналы")
        return

    if not command.args:
        await show_channels(message, session)
        return

    is_numeric = True
    try:
        int(command.args)
    except ValueError:
        is_numeric = False

    if is_numeric:
        channel_id = int(command.args)
        channel_username = ''
    else:
        channel_username = command.args
        channel_id = None

    try:
        chat = await bot.get_chat(channel_id if is_numeric else channel_username)
        channel_id = chat.id
    except:
        await message.answer("Канал не найден")
        return

    is_admin = False
    try:
        chat_member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        is_admin = chat_member.status == ChatMemberStatus.ADMINISTRATOR
    except:
        ...

    if is_admin:
        chan = await session.get(Channel, channel_id)
        if chan:
            await message.answer('Канал уже добавлен')
            return
        else:
            chan = Channel(channel_id=channel_id,
                           link=f'https://t.me/{channel_username.strip("@")}' if channel_username else
                           chat.invite_link,
                           name = chat.full_name)
            session.add(chan)
            await session.commit()
            await message.answer('Канал успешно добавлен')
    else:
        await message.answer('Можно добавлять только каналы, в которых этот бот - админ')


@router.message(Command("chand"))
async def cmd_chand(message: Message, command: CommandObject, session: AsyncSession):
    user = await session.get(User, message.from_user.id)

    if not user.is_admin:
        await message.answer("Только админ может удалять каналы")
        return

    try:
        channel_id = int(command.args)
    except ValueError:
        await message.answer("Нужно отправить id канала, например -123456")

    chan = await session.get(Channel, channel_id)
    if chan:
        await session.delete(chan)
        await session.commit()
        await message.answer("Канал успешно удален")
    else:
        await message.answer("Канала нет в списке")


async def show_channels(message: Message, session: AsyncSession):
    msg = ''
    stmt = select(Channel)
    res = await session.scalars(stmt)
    for chan in res.all():
        msg += f'{chan.name} {chan.channel_id} {chan.link}\n'
    msg = msg.strip()
    if not msg:
        msg = "Каналы не найдены"
    await message.answer(msg)


@router.message(Command('donate'))
async def donate_command(message: Message, command: Command):
    args = command.args

    if not args:
        await message.answer("Укажите сумму")
        return

    amount = 0

    try:
        amount = int(args)
    except:
        ...

    if amount < 20:
        await message.answer("Сумма должна быть целым числом >= 20")
        return

    prices = [LabeledPrice(label="XTR", amount=amount)]
    await message.answer_invoice(
        title='Баскет',
        description='Пополнить счет',
        prices=prices,
        provider_token="",
        payload=f"{amount}_stars",
        currency="XTR"
    )


@router.message(Command('nft'))
async def cmd_nft(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    user = await session.get(User, message.from_user.id)

    if not command.args:
        await show_nfts(message, session)
        return

    if not user.is_admin:
        await message.answer("Только админ может добавлять nft")
        return

    nft = NFT(link=f'https://t.me/nft/{command.args}')
    session.add(nft)
    await session.commit()

    await message.answer('NFT успешно добавлен')


@router.message(Command('nftd'))
async def cmd_nft(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    user = await session.get(User, message.from_user.id)

    if not user.is_admin:
        await message.answer("Только админ может удалять NFT")
        return

    try:
        nft_id = int(command.args)
    except ValueError:
        await message.answer("Нужно отправить id NFT, например 123")

    nft = await session.get(NFT, nft_id)
    if nft and not nft.owner_id:
        await session.delete(nft)
        await session.commit()
        await message.answer("NFT успешно удален")
    else:
        await message.answer("NFT нет в списке")


async def show_nfts(message: Message, session: AsyncSession):
    user = await session.get(User, message.from_user.id)
    msg = ''
    stmt = select(NFT).where(NFT.owner_id == 0)
    res = await session.scalars(stmt)
    for nft in res.all():
        msg += f'{nft.link}'
        if user.is_admin:
            msg += f' {nft.id}'
        msg += '\n'
    msg = msg.strip()
    if not msg:
        msg = "Не найдено свободных NFT"
    await message.answer(msg)


@router.message(Command('nftg'))
async def show_gifted_nfts(message: Message, session: AsyncSession, bot: Bot):
    msg = ''
    stmt = select(NFT).where(NFT.owner_id != 0)
    res = await session.scalars(stmt)
    for nft in res.all():
        chat = await bot.get_chat(nft.owner_id)
        username = f' @{chat.username}' if chat.username else ''
        msg += f'{nft.link} подарен юзеру{username} с id {nft.owner_id}\n'
    msg = msg.strip()
    if not msg:
        msg = "Не найдено подаренных NFT"
    await message.answer(msg)