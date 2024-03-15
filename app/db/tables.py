from piccolo.columns import Text, BigInt
from piccolo.table import Table
from app.config_reader import DB


class Chat(Table, db=DB):
    chat_id = BigInt(required=True, unique=True)
    message_thread_id = BigInt(required=False, null=True)
    chat_type = Text(required=True)


class Project(Table, db=DB):
    repo_url = Text(required=True, unique=True)


PROJECT_TABLES: list = [Project, Chat]
