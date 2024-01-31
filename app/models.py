from typing import Optional, List
from pydantic import BaseModel, Field


class BuiltBy(BaseModel):
    username: str = Field()
    href: str = Field()
    avatar: str = Field()


class Response(BaseModel):
    author: str = Field()
    name: str = Field()
    avatar: str = Field()
    url: str = Field()
    description: Optional[str] = Field(default=None)
    language: Optional[str] = None
    language_color: Optional[str] = Field(alias="languageColor", default=None)
    stars: int = Field()
    forks: int = Field()
    built_by: List[BuiltBy] | None = Field(alias="builtBy", default=[])
