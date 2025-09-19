from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    main_admin_id: int
    main_admin_username: str
    second_admin_id: int
    bot_token: str
    channel_id: int
    channel_link: str
    db_url: str
    db_url_local: str = ""
    database_name: str
    database_username: str
    database_password: str
    premium_gift_1_id: int
    premium_gift_2_id: int
    regular_gift_1_id: int
    regular_gift_2_id: int
    super_gift_id: int


    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
