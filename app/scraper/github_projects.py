import random
import asyncio
import aiohttp
from pydantic import TypeAdapter
from aiogram import Bot, types
from aiogram.enums.parse_mode import ParseMode
from app.models import Response
from app.bot.utils import get_image, make_markdown
from app.db.tables import Project
from app.config_reader import Settings


BOT_MESSAGE: str = "[{name}]({url}) by **{author_name}**\n\n**Description:** _{description}_"


async def get_repos(config: Settings, interval: str = "daily") -> list[Response]:
    async with aiohttp.ClientSession() as session:
        async with session.get(config.github_base_url, params={
            "since": interval
        }) as response:
            adapter = TypeAdapter(list[Response])
            return adapter.validate_python(await response.json())


async def get_github_projects(config: Settings, bot: Bot) -> None:
    response = await get_repos(
        config=config,
        interval=random.choice(["daily", ])  # also can be "weekly" and "monthly"
    )
    for repository in response:
        project = await Project.objects().get_or_create(Project.repo_url == repository.url)

        if not project._was_created:
            continue

        message_limit = 1024 - (31 + len(repository.name) + len(repository.url))
        description = f"{repository.description[:message_limit]}" if repository.description else ""
        if len(description) > message_limit:
            description += "..."

        text = BOT_MESSAGE.format(
            url=make_markdown(repository.url), name=make_markdown(repository.name),
            description=make_markdown(description), author_name=make_markdown(repository.author)
        )
        topic_id = int(config.topic_id) if config.topic_id else None
        await bot.send_photo(
            chat_id=config.chat_id,
            message_thread_id=topic_id,
            photo=types.input_file.FSInputFile(await get_image(repository, bot)),
            caption=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await asyncio.sleep(random.choice([3, 5, 7]))
