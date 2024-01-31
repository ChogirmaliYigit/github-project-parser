import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

from pydantic_settings import BaseSettings

os.environ['PICCOLO_CONF'] = 'app.config_reader'


class Settings(BaseSettings):
    piccolo_conf: str = 'app.config_reader'

    github_base_url: str = "https://api.gitterapp.com/repositories"
    github_access_token: str
    bot_token: str
    chat_id: str
    admins: list[int]
    webhook_base_url: str
    languages: list[str]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


DB = SQLiteEngine('main.db')

APP_REGISTRY = AppRegistry(apps=['app.db.piccolo_app'])
