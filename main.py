from PIL import Image, ImageDraw, ImageFont, ImageChops
import arabic_reshaper
from bidi.algorithm import get_display
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import api_hash, api_id, bot_token, font_path, watermark, gradient, valid_user , Base_dir
import os
app = Client(
    "mohandes_rostami_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token,
)

text_story = list()

def crop_to_4_3(img):
    
    width, height = img.size
    
    target_width = min(width, height * 4 // 3)
    target_height = min(height, width * 3 // 4)
    
    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    
    cropped_img = img.crop((left, top, right, bottom))
    
    return cropped_img



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

        letter_spacing = -2
        line_spacing = 25

        for char in line:
            draw.text((x, y), char, fill=text_color, font=font)

            x += draw.textlength(char, font=font) + letter_spacing
        y += line_height + line_spacing

    return image


def trim_empty_pixel(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    size = im.size

    top_left_pixel = im.getpixel((0, 0))
    bottom_right_pixel = im.getpixel((size[0] - 1, size[1] - 1))

    is_top_left_white = top_left_pixel[0] >= 240 and top_left_pixel[1] >= 240 and top_left_pixel[2]
    is_bottom_right_white = bottom_right_pixel[0] >= 240 and bottom_right_pixel[
        1] >= 240 and bottom_right_pixel[2] >= 240

    is_top_left_transparent = top_left_pixel[3] < 20 if len(
        top_left_pixel) > 3 else False
    is_bottom_right_transparent = bottom_right_pixel[3] < 20 if len(
        bottom_right_pixel) > 3 else False

    if (is_top_left_white and is_bottom_right_white) or (is_top_left_transparent and is_bottom_right_transparent):
        diff = ImageChops.difference(im, bg)
        offset = round(size[1] / 300 * 4)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop((max(bbox[0] - offset, 0), max(bbox[1] - offset, 0), min(bbox[2] + offset, size[0]), min(bbox[3] + offset, size[1])))
        else:
            return im
    else:
        print('No change because no transparency or no white background')
        return im


def compose_images_vertical(image1, image2, watermark, gradient):
    watermark = Image.open(watermark)
    gradient = Image.open(gradient)

    composed_image = Image.new('RGB', (1080, 1920))

    composed_image.paste(image1, (0, 0))
    composed_image.paste(image2, (0, 810))
    composed_image = paste_with_alpha(composed_image, watermark, (300, 673))
    composed_image = paste_with_alpha(composed_image, gradient, (0, 0))

    return composed_image


@app.on_message(filters.command("start"), group=1)
async def start_command(client, message):
    if message.from_user.username not in valid_user:
        await message.reply_text("احراز هویت موفقیت آمیز نبود . لطفا با پشتیبانی (@alinoori1377) ارتباط بگیرید.")
    if message.from_user.username in valid_user:

        text = """
سلام لطفا یکی از گزینه های زیر را انتخاب نمایید
"""
        reply_button = [
            [
                KeyboardButton(text="ارسال عکس"), KeyboardButton(
                    text="خالی کردن حافظه")
            ],
            [
                KeyboardButton(text="ساخت استوری"), KeyboardButton(
                    text="ساخت پست")
            ],
        ]

        reply_markup = ReplyKeyboardMarkup(
            reply_button, one_time_keyboard=True, resize_keyboard=True)

        await client.send_message(chat_id=message.chat.id, text=text, reply_markup=reply_markup)


@app.on_message(filters.regex("ارسال عکس"), group=2)
async def get_pic(client, message):
    await client.send_message(chat_id=message.chat.id, text="لطفا عکس ها را ارسال کنید")

@app.on_message(filters.document, group=3)
async def download_story_pic(client, message):
    last_message = await app.get_messages(message.chat.id, int(message.id)-1)
    if last_message.text == "لطفا عکس ها را ارسال کنید" or str(last_message.media) == "MessageMediaType.DOCUMENT":
        await client.download_media(message)
        await client.send_message(chat_id=message.chat.id, text="عکس ها با موفقیت دانلود شد ")

@app.on_message(filters.regex("ساخت استوری"), group=4)
async def creat_story(client, message):
    await client.send_message(chat_id=message.chat.id, text="متن استوری را ارسال کنید")


@app.on_message(filters.regex("خالی کردن حافظه"), group=5)
async def clear_cach(client, message):
    files = os.listdir(Base_dir + "/downloads")
    [file for file in files if os.remove(Base_dir+f"/downloads/{file}")]
    await app.send_message(message.chat.id , "حافظه با موفقیت خالی شد.")
    
@app.on_message(filters.text, group=6)
async def sent_story_pic(client, message):
    last_message = await app.get_messages(message.chat.id, int(message.id)-1)
    if last_message.text == "متن استوری را ارسال کنید" :
        files = os.listdir(Base_dir + "/downloads")
        for i in range(0, len(files), 2):
            image1_path=Base_dir+ f"/downloads/{files[i]}"
            image2_path=Base_dir+ f"/downloads/{files[i+1]}"
            image1 = resize_with_keep_aspect_ratio(crop_to_4_3(Image.open(image1_path)),1080)
            image2 = resize_with_keep_aspect_ratio(crop_to_4_3(Image.open(image2_path)),1080)
            output_path = f"composed_image_{i}.png"
            image= compose_images_vertical(image1, image2 , watermark , gradient)
            text_image = trim_empty_pixel(creat_text_image(message.text , font_path , 60 , (500,500) , "white"))
            image = paste_with_alpha(image , text_image , ((image.width - text_image.width) // 2 ,1600))
            image.save(output_path)
            os.remove(image1_path)
            os.remove(image2_path)
            await app.send_document(message.chat.id , Base_dir+f"/{output_path}")
            os.remove(Base_dir+f"/{output_path}")


@app.on_message(filters.regex('ساخت پست'), group=7)
async def sent_post_pic(client, message):
    files = os.listdir(Base_dir + "/downloads")
    for i in range(0, len(files)):
        image1_path=Base_dir+ f"/downloads/{files[i]}"
        image1 = resize_with_keep_aspect_ratio(crop_to_4_3(Image.open(image1_path)),1080)
        output_path = f"composed_image_{i}.png"
        watermark_obj = Image.open(watermark)
        image = paste_with_alpha(image1 , resize_with_keep_aspect_ratio(watermark_obj , 310) , (30 , 650))
        image.save(output_path)
        os.remove(image1_path)
        await app.send_document(message.chat.id , Base_dir+f"/{output_path}")
        os.remove(Base_dir+f"/{output_path}")


app.run()
