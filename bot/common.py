from aiogram.filters.callback_data import CallbackData


class ThrowChoiceCallbackFactory(CallbackData, prefix="throw_choice"):
    throws_count: int
    cost: int
    is_premium: bool = False


class NFTGiftCallbackFactory(CallbackData, prefix='nft'):
    user_id: int
    nft_id: int
