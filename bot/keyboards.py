from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.common import ThrowChoiceCallbackFactory, NFTGiftCallbackFactory
from bot.answer_texts import get_invitation
from bot.config_reader import config


def get_main_inline_keyboard(free_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    free_throws_text = f'Бесплатные броски {free_count}' if free_count else \
        'Бесплатные броски будут завтра'
    free_throws_callback_data = ThrowChoiceCallbackFactory(throws_count=6, cost=0).pack() \
        if free_count else 'no_free_left'
    builder.row(InlineKeyboardButton(text=free_throws_text,
                callback_data=free_throws_callback_data))
    builder.row(InlineKeyboardButton(text='🏀 5 мячей · 1 ⭐',
                callback_data=ThrowChoiceCallbackFactory(throws_count=5, cost=1).pack()),
                 InlineKeyboardButton(text='🏀 3 мяча · 5 ⭐',
                callback_data=ThrowChoiceCallbackFactory(throws_count=3, cost=5).pack()))
    builder.row(InlineKeyboardButton(text='🏀 2 мяча · 8 ⭐',
                callback_data=ThrowChoiceCallbackFactory(throws_count=2, cost=8).pack()),
                 InlineKeyboardButton(text='🏀 1 мяч · 10 ⭐',
                callback_data=ThrowChoiceCallbackFactory(throws_count=1, cost=10).pack()))
    builder.row(InlineKeyboardButton(text='💎🏀 1 мяч · 15 ⭐',
                callback_data=ThrowChoiceCallbackFactory(throws_count=1, cost=15, is_premium=True).pack()),
                 InlineKeyboardButton(text='+15 🏀 за друга',
                callback_data='invite'))
    builder.row(InlineKeyboardButton(text='Победители NFT 🏆', url=config.channel_link))
    return builder.as_markup()


def get_inline_keyboard_for_free_step(channels_links: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for link in channels_links:
        builder.row(InlineKeyboardButton(text='Подписаться', url=link))
    builder.row(InlineKeyboardButton(text='Проверить', callback_data='check'))
    return builder.as_markup()


def get_invite_markup(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Пригласить друга', url=get_invitation(user_id)))
    return builder.as_markup()


def get_nft_gift_markup(nft_id: int, winner_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Отправлено, запостить в канал',
                    callback_data=NFTGiftCallbackFactory(user_id=winner_id,
                                    nft_id=nft_id).pack()))
    return builder.as_markup()
