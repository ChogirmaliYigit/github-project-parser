from typing import List

from piccolo.columns import Text
from piccolo.table import Table
from app.config_reader import DB


class Project(Table, db=DB):
    repo_url = Text(required=True, unique=True)


PROJECT_TABLES: List[Table] = [Project]
