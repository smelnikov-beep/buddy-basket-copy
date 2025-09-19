from bot.db.models import User, NFT
from bot.config_reader import config


def get_main_answer_text(stars_count: int) -> str:
    answer_text = '🏀 Попади каждым броском в кольцо и получи крутой <a href="https://telegra.ph/Poluchaj-Telegram-podarki-za-kazhduyu-pobedu-09-08-2">подарок, подробнее.</a>'
    answer_text += '\n\n<b>🏆 Выпал кубок - приз NFT подарок.</b>'
    answer_text += f'\nШанс выпадения кубка есть только у тех кто подписан на @{config.channel_link.split("/")[-1]}'
    answer_text += f'\n\n⭐ Баланс: <b>{stars_count}</b>'
    answer_text += f'\n💫 Купить звёзды @{config.main_admin_username}'

    return answer_text


NO_FREE_LEFT_TEXT = '''Вы использовали все бесплатные броски на сегодня. <b>Возвращайтесь завтра за новыми!</b>

Получайте +15 🏀 за каждого друга бесплатно.
Условие: друг должен сыграть 3 раза.'''


GET_REFERER_STARS_TEXT = 'Вы получили 3 звезды за друга'

INVOICE_TEXT = 'Оплачивая, вы подтверждаете что ознакомились с правилами игры и даете свое согласие на участие: NFT дарится только при выпадении кубка, кубок выпадает случайно в случае победы 🏆'

INVITE_TEXT = '''Получай +15 🏀 за каждого друга!
Условие: друг должен сыграть 3 раза.'''


def get_invitation(user_id: int) -> str:
    return f'''https://t.me/share/url?url=Попадешь в кольцо? NFT подарки дарят.
https://t.me/Buddy_basket_copy_bot?start={user_id}'''


def get_win_text(user: User, nft: NFT) -> str:
    name = f' {user.name}' if user.name else ''
    username = f' @{user.username}' if user.username else ''
    return f'''Пользователь{name}{username} с id {user.user_id} выигрывает крутую NFT!

🏀 Баскет @Buddy_basket_copy_bot

{nft.link}'''


NO_USERNAME_TEXT = 'Добавьте «Имя пользователя» (username) в своем профиле, чтобы мы могли дарить Вам подарки.'