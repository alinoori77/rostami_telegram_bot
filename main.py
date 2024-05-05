from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from pyrogram import Client, filters
from config import api_hash, api_id, bot_token, font_path, watermark, gradient
import os
app = Client(
    "mohandes_rostami_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token,
)


def resize_with_keep_aspect_ratio(image, width_size):

    width, height = image.size

    ratio = height/width

    final_image = image.resize((width_size, int(width_size*ratio)))

    return final_image


def paste_with_alpha(background, overlay, position):
    if overlay.mode != 'RGBA':
        overlay = overlay.convert('RGBA')

    new_image = Image.new('RGBA', background.size)

    new_image.paste(background, (0, 0))

    new_image.paste(overlay, position, overlay)

    return new_image


def creat_text_image(text, font_path, font_size, position, text_color):

    image = Image.new('RGBA', (1080, 1920))

    font = ImageFont.truetype(font_path, font_size)

    draw = ImageDraw.Draw(image)

    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    bbox = draw.textbbox(position, bidi_text, font=font)

    text_width = bbox[2] - bbox[0]

    position = (position[0] - text_width / 2, position[1])
    lines = bidi_text.split('\n')
    y = position[1]

    for line in lines:
        line_width = draw.textlength(line, font=font)
        line_height = font_size
        x = position[0]

        x += (text_width - line_width) / 2

        letter_spacing = -1
        line_spacing = 25

        for char in line:
            draw.text((x, y), char, fill=text_color, font=font)

            x += draw.textlength(char, font=font) + letter_spacing
        y += line_height + line_spacing

    return image


def compose_images_vertical(image1_path, image2_path, watermark, gradient):
    image1 = resize_with_keep_aspect_ratio(image1_path, 1080)
    image2 = resize_with_keep_aspect_ratio(image2_path, 1080)
    watermark = Image.open(watermark)
    gradient = Image.open(gradient)

    composed_image = Image.new('RGB', (1080, 1920))

    composed_image.paste(image1, (-60, 0))
    composed_image.paste(image2, (-60, 800))
    composed_image = paste_with_alpha(composed_image, watermark, (300, 563))
    composed_image = paste_with_alpha(composed_image, gradient, (0, 0))

    return composed_image


# ali =creat_text_image("علی نوری" ,(font_path) , 60 , (500,500) , "white")
# ali.save("./test.png")
