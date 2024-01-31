import asyncio
import io
import random

import aiohttp
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
from app.models import Response


TEMPLATE_IMAGE_PATH = "template.jpg"
ESCAPE_CHARS_MARKDOWN = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
POWERED_BY = "Powered by {}"


async def get_repo_detail(repo: Response) -> tuple:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/users/{repo.author}/followers") as response:
            followers = len(await response.json()) if type(await response.json()) is list else 0

        await asyncio.sleep(random.choice([4, 5, 6]))

        async with session.get(f"https://api.github.com/repos/{repo.author}/{repo.name}/issues") as response:
            issues = len(await response.json())

        await asyncio.sleep(random.choice([4, 5, 6]))

        async with session.get(f"https://api.github.com/repos/{repo.author}/{repo.name}/topics") as response:
            data = await response.json()
            topics = ""
            for topic in data.get("names", []):
                topic = f"#{topic} "
                if 55 - len(topics.split("\n")[-1]) <= len(topic):
                    topics += "\n"
                topics += topic
                if topics.count("\n") == 3:
                    break

        return followers, issues, topics


async def get_rounded_image(img_link: str, width: int, height: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_link) as response:
            img = Image.open(io.BytesIO(await response.read()))
            img = img.resize((width, height)).convert("RGBA")

            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, width, height), fill=255)

            img.putalpha(mask)
            return img


async def get_image(repo: Response, bot: Bot):
    bot_properties = await bot.get_me()
    followers, issues, topics = await get_repo_detail(repo)

    output_path = f"assets/result_{repo.author}_{repo.name}.jpg"
    base_image = Image.open(TEMPLATE_IMAGE_PATH)

    img = await get_rounded_image(repo.avatar, width=100, height=100)
    base_image.paste(img, (20, 20), img)

    result_image = Image.new("RGB", base_image.size, (255, 255, 255))
    result_image.paste(base_image, (0, 0), base_image)

    draw = ImageDraw.Draw(result_image)

    # Repository name
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=25)
    draw.text((135, 25), repo.name, font=font, fill="white")

    # Owner name and followers
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=18)
    text = f"by {repo.author}"
    if followers:
        text += f" ({await make_number_readable(followers)} followers)"
    draw.text(
        (135, 75),
        text,
        font=font,
        fill="gray"
    )

    # Repository's language
    if repo.language:
        font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=15)
        draw.text((135, 110), repo.language, font=font, fill=repo.language_color or "white")

    # Repository's stars
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17)
    draw.text((52, 235), await make_number_readable(repo.stars), font=font, fill="white")

    # Repository's forks
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17)
    draw.text((170, 235), await make_number_readable(repo.forks), font=font, fill="white")

    # Repository's open issues
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17)
    draw.text((300, 235), await make_number_readable(issues), font=font, fill="white")

    # Repository's contributors
    font = ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17)
    draw.text((400, 235), await make_number_readable(len(repo.built_by)), font=font, fill="white")

    # Repository's topics
    font = ImageFont.truetype("fonts/Roboto-Bold.ttf", size=18)
    draw.text((30, 285), topics, font=font, fill="blue", antialias=True)

    # Built by users
    start_position_x = 30
    start_position_y = 410
    count = 0
    for user in repo.built_by:
        if count == 30:
            break

        img = await get_rounded_image(user.avatar, width=60, height=60)
        result_image.paste(img, (start_position_x, start_position_y), img)

        if count != 0 and count % 10 == 0:
            start_position_x = 30
            start_position_y += 65
        else:
            start_position_x += 65

        count += 1

    # Powered by text
    font = ImageFont.truetype("fonts/Roboto-Bold.ttf", size=15)
    draw.text(
        (60, 600),
        POWERED_BY.format(f"https://t.me/{bot_properties.username}"),
        font=font,
        fill="white"
    )

    result_image.save(output_path, quality=95)
    return output_path


def make_markdown(text):
    result = ""
    for letter in text:
        if letter in ESCAPE_CHARS_MARKDOWN:
            result += f'\{letter}'
        else:
            result += letter
    return result


async def make_number_readable(number: int) -> str:
    number = str(number)

    if len(number) <= 3:
        return number

    elif len(number) <= 6:
        return "%.2f" % (int(number) / 1000) + "K"

    elif len(number) <= 9:
        return "%.2f" % (int(number) / 10000) + "M"
