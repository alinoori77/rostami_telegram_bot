from PIL import Image, ImageDraw, ImageFont , ImageChops
import arabic_reshaper
from bidi.algorithm import get_display
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup , KeyboardButton
from config import api_hash, api_id, bot_token, font_path, watermark, gradient , valid_user
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

def trim_empty_pixel(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    size = im.size
    
    top_left_pixel = im.getpixel((0,0))
    bottom_right_pixel = im.getpixel((size[0] - 1, size[1] - 1))
    
    is_top_left_white = top_left_pixel[0] >= 240 and top_left_pixel[1] >= 240 and top_left_pixel[2]
    is_bottom_right_white = bottom_right_pixel[0] >= 240 and bottom_right_pixel[1] >= 240 and bottom_right_pixel[2] >= 240
    
    is_top_left_transparent = top_left_pixel[3] < 20 if len(top_left_pixel) > 3 else False
    is_bottom_right_transparent = bottom_right_pixel[3] < 20 if len(bottom_right_pixel) > 3 else False
    
    if (is_top_left_white and is_bottom_right_white) or (is_top_left_transparent and is_bottom_right_transparent):
        diff = ImageChops.difference(im, bg)
        offset = round(size[1] / 300 * 4);
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop((max(bbox[0] - offset, 0), max(bbox[1] - offset, 0), min(bbox[2] + offset, size[0]), min(bbox[3] + offset, size[1])))
        else:
            return im
    else:
        print('No change because no transparency or no white background')
        return im


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



@app.on_message(filters.command("start") , group=1)
async def start_command (client, message):
    if message.from_user.username not in valid_user :
        await message.reply_text("احراز هویت موفقیت آمیز نبود . لطفا با پشتیبانی (@alinoori1377) ارتباط بگیرید.")
    if message.from_user.username in valid_user :

        text="""
سلام لطفا یکی از گزینه های زیر را انتخاب نمایید
"""
        reply_button =  [
            [
                KeyboardButton(text = "ارسال عکس") , KeyboardButton(text = "خالی کردن حافظه")
            ],
            [
                KeyboardButton(text = "ساخت استوری") , KeyboardButton(text = "ساخت پست")
            ],
        ]

        reply_markup = ReplyKeyboardMarkup(reply_button , one_time_keyboard=True , resize_keyboard=True)

        await client.send_message(chat_id=message.chat.id , text=text , reply_markup= reply_markup)

@app.on_message(filters.regex("ساخت استوری"))
async def story (client, message):
    await client.send_message(chat_id=message.chat.id , text="لطفا عکس های استوری را ارسال کنید")

@app.on_message(filters.document)
async def download_story_pic (client, message):
    last_message = await app.get_messages(message.chat.id, int(message.id)-1)
    if last_message.text == "لطفا عکس های استوری را ارسال کنید":
        print("sagh")

    # if (int(message.id)-1)
    # print(message)
    # await client.send_message(chat_id=message.chat.id , text="بی پدر ")


# @app.on_message(filters.regex("متن استوری را ارسال نمایید") and filters.text)
# async def story (client, message):
#     await client.send_message(chat_id=message.chat.id , text="بی پدر ")

app.run()