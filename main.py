from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from pyrogram import Client ,filters
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton
from config import api_hash , api_id , bot_token , font_path , watermark , gradient
import os