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
        interval=random.choice(["daily",])  # also can be "weekly" and "monthly"
    )
    for repository in response:
        project = await Project.objects().get_or_create(Project.repo_url == repository.url)

        if not project._was_created:
            continue

        message_limit = 1008
        description = repository.description[:message_limit]
        if len(description) > message_limit:
            description += "..."

        topic_id = int(config.topic_id) if config.topic_id else None
        await bot.send_photo(
            chat_id=config.chat_id,
            message_thread_id=topic_id,
            photo=types.input_file.FSInputFile(await get_image(repository, bot)),
            caption=f"**Description:** _{make_markdown(description)}_",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await asyncio.sleep(random.choice([3, 5, 7]))
