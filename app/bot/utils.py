import io
from datetime import datetime

import aiohttp
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot
from app.models import Response

TEMPLATE_IMAGE_PATH = "template.jpg"
ESCAPE_CHARS_MARKDOWN = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
POWERED_BY = "Powered by {} | {}"


async def get_repo_detail(repo: Response) -> tuple:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.github.com/repos/{repo.author}/{repo.name}/issues") as response:
            issues = len(await response.json())

        async with session.get(f"https://api.github.com/repos/{repo.author}/{repo.name}/topics") as response:
            data = await response.json()
            topics = ""
            max_length = 45
            for topic in data.get("names", []):
                topics += f"#{topic} "
                if len(topics) >= max_length:
                    break

            topics = topics.strip()
            if len(topics) > max_length:
                topics = topics[:max_length] + "..."

        return issues, topics


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
    issues, topics = await get_repo_detail(repo)

    output_path = f"assets/result_{repo.author}_{repo.name}.jpg"
    base_image = Image.open(TEMPLATE_IMAGE_PATH)

    img = await get_rounded_image(repo.avatar, width=100, height=100)
    base_image.paste(img, (20, 20), img)

    result_image = Image.new("RGB", base_image.size, (255, 255, 255))
    result_image.paste(base_image, (0, 0), base_image)

    draw = ImageDraw.Draw(result_image)

    # Repository name
    draw.text(
        (135, 25),
        repo.name,
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=25),
        fill="white"
    )

    # Owner name and followers
    draw.text(
        (135, 75),
        f"by {repo.author}",
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=18),
        fill="gray"
    )

    # Repository's language
    if repo.language:
        draw.text(
            (135, 110),
            repo.language,
            font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=15),
            fill=repo.language_color or "white"
        )

    # Repository's stars
    draw.text(
        (52, 235),
        await make_number_readable(repo.stars),
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17),
        fill="white"
    )

    # Repository's forks
    draw.text(
        (170, 235),
        await make_number_readable(repo.forks),
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17),
        fill="white"
    )

    # Repository's open issues
    draw.text(
        (300, 235),
        await make_number_readable(issues),
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17),
        fill="white"
    )

    # Repository's contributors
    draw.text(
        (400, 235),
        await make_number_readable(len(repo.built_by)),
        font=ImageFont.truetype("fonts/Roboto-Regular.ttf", size=17),
        fill="white"
    )

    # Repository's topics
    draw.text(
        (30, 285),
        topics,
        font=ImageFont.truetype("fonts/Roboto-Bold.ttf", size=18),
        fill="white",
    )

    # Built by users
    start_position_x = 30
    start_position_y = 285 if not topics else 320
    max_length = 7
    for user in repo.built_by[:max_length]:
        img = await get_rounded_image(user.avatar, width=50, height=50)
        result_image.paste(img, (start_position_x, start_position_y), img)
        start_position_x += 55

    if len(repo.built_by) > max_length:
        draw.ellipse([(420, start_position_y), (470, start_position_y + 50)], fill="#050A30")
        draw.text(
            (430, start_position_y + 20),
            f"+ {await make_number_readable(len(repo.built_by[max_length:]))}",
            font=ImageFont.truetype("fonts/Roboto-Bold.ttf", size=12),
            fill="white"
        )

    # Powered by text
    draw.text(
        (40, 450),
        POWERED_BY.format(f"@{bot_properties.username}", datetime.now().strftime("%d.%m.%Y, %H:%M:%S")),
        font=ImageFont.truetype("fonts/Roboto-Bold.ttf", size=15),
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
