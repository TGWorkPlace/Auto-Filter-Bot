import asyncio
import re
import ast
import math
import random
import pytz
from datetime import datetime, timedelta, date, time
lock = asyncio.Lock()
from database.users_chats_db import db
from database.refer import referdb
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from info import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, WebAppInfo
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import *
from fuzzywuzzy import process
from database.users_chats_db import db
from database.ia_filterdb import Media, Media2, get_file_details, get_search_results, get_bad_files
import logging
from urllib.parse import quote_plus
from Lucia.util.file_properties import get_name, get_hash, get_media_file_size
from database.topdb import silentdb
import requests
import string
import tracemalloc
from pyrogram.enums import ParseMode, ButtonStyle
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

tracemalloc.start()

TIMEZONE = "Asia/Kolkata"
BUTTON = {}
BUTTONS = {}
FRESH = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if EMOJI_MODE:
        await message.react(emoji=random.choice(REACTIONS))
    await silentdb.update_top_messages(message.from_user.id, message.text)
    if message.chat.id != SUPPORT_CHAT_ID:
        settings = await get_settings(message.chat.id)
        if settings['auto_ffilter']:
            if re.search(r'https?://\S+|www\.\S+|t\.me/\S+', message.text):
                if await is_check_admin(client, message.chat.id, message.from_user.id):
                    return
                return await message.delete()   
            await auto_filter(client, message)
    else:
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention},\n\nʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀᴠᴀɪʟᴀʙʟᴇ ✅\n\n📂 ꜰɪʟᴇꜱ ꜰᴏᴜɴᴅ : {str(total_results)}\n🔍 ꜱᴇᴀʀᴄʜ :</b> <code>{search}</code>\n\n<b>‼️ ᴛʜɪs ɪs ᴀ <u>sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</u> sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\n📝 ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ : 👇</b>",   
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 ᴊᴏɪɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ʜᴇʀᴇ 🔎", url=GRP_LNK)]]))


@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    bot_id = bot.me.id
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if EMOJI_MODE:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    if content.startswith(("/", "#")):
        return  
    try:
        await silentdb.update_top_messages(user_id, content)
        pm_search = await db.pm_search_status(bot_id)
        if pm_search:
            await auto_filter(bot, message)
        else:
            await message.reply_text(
             text=f"<b><i>ɪ ᴀᴍ ɴᴏᴛ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ 🚫 ᴊᴏɪɴ ᴍʏ ɢʀᴏᴜᴘ ꜰʀᴏᴍ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴀɴᴅ ꜱᴇᴀʀᴄʜ ᴛʜᴇʀᴇ !</i></b>",   
             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📝 ꜱᴇᴀʀᴄʜʜᴇʀᴇ ", url=GRP_LNK, style=ButtonStyle.PRIMARY)]])
            )
    except Exception as e:
        print(f"An error occurred: {str(e)}")


@Client.on_callback_query(filters.regex(r"^reffff"))
async def refercall(bot, query):
    btn = [[
        InlineKeyboardButton('ɪɴᴠɪᴛᴇ ɪɪɴᴋ', url=f'https://telegram.me/share/url?url=https://t.me/{bot.me.username}?start=reff_{query.from_user.id}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83'),
        InlineKeyboardButton(f'⏳ {referdb.get_refer_points(query.from_user.id)}', callback_data='ref_point'),
        InlineKeyboardButton('ʙᴀᴄᴋ', callback_data='premium')
    ]]
    reply_markup = InlineKeyboardMarkup(btn)
    await bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
        )
    await query.message.edit_text(
        text=f'Hay Your refer link:\n\nhttps://t.me/{bot.me.username}?start=reff_{query.from_user.id}\n\nShare this link with your friends, Each time they join,  you will get 10 refferal points and after 100 points you will get 1 month premium subscription.',
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
        )
    await query.answer()


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    try:
        ident, req, key, offset = query.data.split("_")
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        if int(req) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        try:
            offset = int(offset)
        except:
            offset = 0
        if BUTTONS.get(key)!=None:
            search = BUTTONS.get(key)
        else:
            search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
        try:
            n_offset = int(n_offset)
        except:
            n_offset = 0
        if not files:
            return
        temp.GETALL[key] = files
        temp.SHORT[query.from_user.id] = query.message.chat.id
        settings = await get_settings(query.message.chat.id)
        if settings.get('button'):
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}', style=ButtonStyle.PRIMARY
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [ 
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER) 
            ])
        try:
            if settings['max_btn']:
                if 0 < offset <= 10:
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - 10
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages", style=ButtonStyle.DANGER)]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)
                        ],
                    )
            else:
                if 0 < offset <= int(MAX_B_TN):
                    off_set = 0
                elif offset == 0:
                    off_set = None
                else:
                    off_set = offset - int(MAX_B_TN)
                if n_offset == 0:
                    btn.append(
                        [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                    )
                elif off_set is None:
                    btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)])
                else:
                    btn.append(
                        [
                            InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS),
                            InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                            InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)
                        ],
                    )
        except KeyError:
            await save_group_settings(query.message.chat.id, 'max_btn', True)
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⋞ ʙᴀᴄᴋ", callback_data=f"next_{req}_{key}_{off_set}", style=ButtonStyle.SUCCESS),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)
                    ],
                )
        if not settings.get('button'):
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Next Funtion - {e}")

@Client.on_callback_query(filters.regex(r"^qualities#"))
async def qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        offset = int(offset)
        search = search.replace(' ', '_')
        btn = []
        for i in range(0, len(QUALITIES)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=QUALITIES[i].title(),
                    callback_data=f"fq#{QUALITIES[i].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
                InlineKeyboardButton(
                    text=QUALITIES[i+1].title(),
                    callback_data=f"fq#{QUALITIES[i+1].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ ǫᴜᴀʟɪᴛʏ ⇊", callback_data="ident", style=ButtonStyle.DANGER
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fq#homepage#{key}#{offset}", style=ButtonStyle.SUCCESS)])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Quality Callback Handler - {e}")

@Client.on_callback_query(filters.regex(r"^fq#"))
async def filter_qualities_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, qual, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = qual in search
        if baal:
            search = search.replace(qual, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if qual != "homepage":
            search = f"{search} {qual}"
            BUTTONS[key] = search
        else:
            search = FRESH.get(key, search)
            BUTTONS[key] = search
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings.get('button'):
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}', style=ButtonStyle.PRIMARY
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [ 
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages", style=ButtonStyle.DANGER)]
            )               
        if not settings.get('button'):
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Quality - {e}")

@Client.on_callback_query(filters.regex(r"^languages#"))
async def languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        search = search.replace(' ', '_')
        offset = int(offset)
        btn = []
        for i in range(0, len(LANGUAGES)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=LANGUAGES[i].title(),
                    callback_data=f"fl#{LANGUAGES[i].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
                InlineKeyboardButton(
                    text=LANGUAGES[i+1].title(),
                    callback_data=f"fl#{LANGUAGES[i+1].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ ⇊", callback_data="ident", style=ButtonStyle.DANGER
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fl#homepage#{key}#{offset}", style=ButtonStyle.SUCCESS)])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Language Cb Handaler - {e}")
    

@Client.on_callback_query(filters.regex(r"^fl#"))
async def filter_languages_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, lang, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = lang in search
        if baal:
            search = search.replace(lang, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if lang != "homepage":
            search = f"{search} {lang}"
            BUTTONS[key] = search
        else:
            search = FRESH.get(key, search)
            BUTTONS[key] = search
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings.get('button'):
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}', style=ButtonStyle.PRIMARY
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages", style=ButtonStyle.DANGER)]
            )    

        if not settings.get('button'):
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Language - {e}")
        
@Client.on_callback_query(filters.regex(r"^seasons#"))
async def season_cb_handler(client: Client, query: CallbackQuery):
    try:
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        _, key, offset = query.data.split("#")
        search = FRESH.get(key)
        search = search.replace(' ', '_')
        offset = int(offset)
        btn = []
        for i in range(0, len(SEASONS)-1, 2):
            btn.append([
                InlineKeyboardButton(
                    text=SEASONS[i].title(),
                    callback_data=f"fs#{SEASONS[i].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
                InlineKeyboardButton(
                    text=SEASONS[i+1].title(),
                    callback_data=f"fs#{SEASONS[i+1].lower()}#{key}#{offset}",
                    style=ButtonStyle.PRIMARY
                ),
            ])
        btn.insert(
            0,
            [
                InlineKeyboardButton(
                    text="⇊ ꜱᴇʟᴇᴄᴛ Sᴇᴀsᴏɴ ⇊", callback_data="ident", style=ButtonStyle.DANGER
                )
            ],
        )
        req = query.from_user.id
        offset = 0
        btn.append([InlineKeyboardButton(text="↭ ʙᴀᴄᴋ ᴛᴏ ꜰɪʟᴇs ↭", callback_data=f"fl#homepage#{key}#{offset}", style=ButtonStyle.SUCCESS)])
        await query.edit_message_reply_markup(InlineKeyboardMarkup(btn))
    except Exception as e:
        print(f"Error In Season Cb Handaler - {e}")


@Client.on_callback_query(filters.regex(r"^fs#"))
async def filter_season_cb_handler(client: Client, query: CallbackQuery):
    try:
        _, seas, key, offset = query.data.split("#")
        offset = int(offset)
        curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
        search = FRESH.get(key)
        search = search.replace("_", " ")
        baal = seas in search
        if baal:
            search = search.replace(seas, "")
        else:
            search = search
        req = query.from_user.id
        chat_id = query.message.chat.id
        message = query.message
        try:
            if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
                return await query.answer(
                    f"⚠️ ʜᴇʟʟᴏ {query.from_user.first_name},\nᴛʜɪꜱ ɪꜱ ɴᴏᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ,\nʀᴇǫᴜᴇꜱᴛ ʏᴏᴜʀ'ꜱ...",
                    show_alert=True,
                )
        except:
            pass
        if seas != "homepage":
            search = f"{search} {seas}"
            BUTTONS[key] = search
        else:
            search = FRESH.get(key, search)
            BUTTONS[key] = search
        files, n_offset, total_results = await get_search_results(chat_id, search, offset=offset, filter=True)
        if not files:
            await query.answer("🚫 ɴᴏ ꜰɪʟᴇꜱ ᴡᴇʀᴇ ꜰᴏᴜɴᴅ 🚫", show_alert=1)
            return
        temp.GETALL[key] = files
        settings = await get_settings(message.chat.id)
        if settings.get('button'):
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {clean_filename(file.file_name)}", callback_data=f'file#{file.file_id}', style=ButtonStyle.PRIMARY
                    ),
                ]
                for file in files
            ]
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        else:
            btn = []
            btn.insert(0, 
                [
                    InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                    InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ",  callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
                ]
            )
            btn.insert(1, [
                InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
                InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
            ])
        if n_offset != "":
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
                else:
                    btn.append(
                        [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟",callback_data=f"next_{req}_{key}_{n_offset}", style=ButtonStyle.SUCCESS)]
                )
        else:
            n_offset = 0
            btn.append(
                [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭",callback_data="pages", style=ButtonStyle.DANGER)]
            )    

        if not settings.get('button'):
            cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
            time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
            remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
            cap = await get_cap(settings, remaining_seconds, files, query, total_results, search, offset)
            try:
                await query.message.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
            except MessageNotModified:
                pass
        else:
            try:
                await query.edit_message_reply_markup(
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except MessageNotModified:
                pass
        await query.answer()
    except Exception as e:
        print(f"Error In Season - {e}")


async def auto_filter(client, msg, spoll=False):
    curr_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    if not spoll:
        message = msg
        if message.text.startswith("/"): return
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            search = search.lower()
            m = await message.reply_text(f'<b>Wᴀɪᴛ {message.from_user.mention} Sᴇᴀʀᴄʜɪɴɢ Yᴏᴜʀ Qᴜᴇʀʏ :<i>{search}...</i></b>', reply_to_message_id=message.id)
            find = search.split(" ")
            search = ""
            removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file"]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            search = search.replace("-", " ")
            search = search.replace(":","")
            search = re.sub(r'\s+', ' ', search).strip()
            files, offset, total_results = await get_search_results(message.chat.id, search, offset=0, filter=True)
            settings = await get_settings(message.chat.id)
            if not files:
                if settings["spell_check"]:
                    ai_sts = await m.edit('🤖 ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ, ᴀɪ ɪꜱ ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ...')
                    is_misspelled = await ai_spell_check(chat_id=message.chat.id, wrong_name=search)
                    if is_misspelled:
                        await ai_sts.edit(f'<b>✅Aɪ Sᴜɢɢᴇsᴛᴇᴅ ᴍᴇ<code> {is_misspelled}</code> \nSᴏ Iᴍ Sᴇᴀʀᴄʜɪɴɢ ғᴏʀ <code>{is_misspelled}</code></b>')
                        await asyncio.sleep(2)
                        message.text = is_misspelled
                        await ai_sts.delete()
                        return await auto_filter(client, message)
                    await ai_sts.delete()
                    return await advantage_spell_chok(client, message)
        else:
            return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
        m = await message.reply_text(f'<b>Wᴀɪᴛ {message.from_user.mention} Sᴇᴀʀᴄʜɪɴɢ Yᴏᴜʀ Qᴜᴇʀʏ :<i>{search}...</i></b>', reply_to_message_id=message.id)
        settings = await get_settings(message.chat.id)
        await msg.message.delete()

    key = f"{message.chat.id}-{message.id}"
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id

    if settings.get('button'):
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{silent_size(file.file_size)}| {extract_tag(file.file_name)} {clean_filename(file.file_name)}",
                    callback_data=f'file#{file.file_id}',
                    style=ButtonStyle.PRIMARY
                ),
            ]
            for file in files
        ]
        btn.insert(0,
            [
                InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ", callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
            ]
        )
        btn.insert(1, [
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
            InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
        ])
    else:
        btn = []
        btn.insert(0,
            [
                InlineKeyboardButton("ᴘɪxᴇʟ", callback_data=f"qualities#{key}#0", style=ButtonStyle.SECONDARY),
                InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇ", callback_data=f"languages#{key}#0", style=ButtonStyle.SECONDARY),
                InlineKeyboardButton("ꜱᴇᴀꜱᴏɴ", callback_data=f"seasons#{key}#0", style=ButtonStyle.SECONDARY)
            ]
        )
        btn.insert(1, [
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/AM_FILMS", style=ButtonStyle.DANGER),
            InlineKeyboardButton("📥 Sᴇɴᴅ Aʟʟ 📥", callback_data=f"sendfiles#{key}", style=ButtonStyle.DANGER)
        ])

    if offset != "":
        req = message.from_user.id if message.from_user else 0
        try:
            if settings['max_btn']:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}", style=ButtonStyle.SUCCESS)]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}", style=ButtonStyle.SUCCESS)]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("ᴘᴀɢᴇ", callback_data="pages", style=ButtonStyle.DANGER), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="ɴᴇxᴛ ⋟", callback_data=f"next_{req}_{key}_{offset}", style=ButtonStyle.SUCCESS)]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="↭ ɴᴏ ᴍᴏʀᴇ ᴘᴀɢᴇꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ↭", callback_data="pages", style=ButtonStyle.DANGER)]
        )

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    cur_time = datetime.now(pytz.timezone('Asia/Kolkata')).time()
    time_difference = timedelta(hours=cur_time.hour, minutes=cur_time.minute, seconds=(cur_time.second+(cur_time.microsecond/1000000))) - timedelta(hours=curr_time.hour, minutes=curr_time.minute, seconds=(curr_time.second+(curr_time.microsecond/1000000)))
    remaining_seconds = "{:.2f}".format(time_difference.total_seconds())
    TEMPLATE = script.IMDB_TEMPLATE_TXT
    if imdb:
        cap = TEMPLATE.format(
            qurey=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
        temp.IMDB_CAP[message.from_user.id] = cap
        if not settings.get('button'):
            for file_num, file in enumerate(files, start=1):
                cap += f"\n\n<b>{file_num}. <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>{get_size(file.file_size)} | {clean_filename(file.file_name)}</a></b>"
    else:
        if settings.get('button'):
            cap = f"<b><blockquote>Hᴇʏ,{message.from_user.mention}</blockquote>\n\n📂 Hᴇʀᴇ I Fᴏᴜɴᴅ Fᴏʀ Yᴏᴜʀ Sᴇᴀʀᴄʜ <code>{search}</code></b>\n\n"
        else:
            cap = f"<b><blockquote>Hᴇʏ,{message.from_user.mention}</blockquote>\n\n📂 Hᴇʀᴇ I Fᴏᴜɴᴅ Fᴏʀ Yᴏᴜʀ Sᴇᴀʀᴄʜ <code>{search}</code></b>\n\n"
            for file_num, file in enumerate(files, start=1):
                cap += f"<b>{file_num}. <a href='https://telegram.me/{temp.U_NAME}?start=file_{message.chat.id}_{file.file_id}'>{get_size(file.file_size)} | {clean_filename(file.file_name)}\n\n</a></b>"

    if imdb and imdb.get('poster'):
        try:
            hehe = await m.edit_photo(photo=imdb.get('poster'), caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await m.edit_photo(photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await m.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), parse_mode=enums.ParseMode.HTML)
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(DELETE_TIME)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(DELETE_TIME)
                await fek.delete()
                await message.delete()
    else:
        fuk = await m.edit_text(text=cap, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        try:
            if settings['auto_delete']:
                await asyncio.sleep(DELETE_TIME)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(DELETE_TIME)
            await fuk.delete()
            await message.delete()


async def ai_spell_check(chat_id, wrong_name):
    async def search_movie(wrong_name):
        search_results = imdb.search_movie(wrong_name)
        movie_list = [movie['title'] for movie in search_results]
        return movie_list
    movie_list = await search_movie(wrong_name)
    if not movie_list:
        return
    for _ in range(5):
        closest_match = process.extractOne(wrong_name, movie_list)
        if not closest_match or closest_match[1] <= 80:
            return
        movie = closest_match[0]
        files, offset, total_results = await get_search_results(chat_id=chat_id, query=movie)
        if files:
            return movie
        movie_list.remove(movie)


async def advantage_spell_chok(client, message):
    mv_id = message.id
    search = message.text
    chat_id = message.chat.id
    settings = await get_settings(chat_id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", message.text, flags=re.IGNORECASE)
    query = query.strip() + " movie"
    try:
        movies = await get_poster(search, bulk=True)
    except:
        k = await message.reply(script.I_CUDNT.format(message.from_user.mention))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    if not movies:
        google = search.replace(" ", "+")
        button = [[
            InlineKeyboardButton("🔍 ᴄʜᴇᴄᴋ sᴘᴇʟʟɪɴɢ ᴏɴ ɢᴏᴏɢʟᴇ 🔍", url=f"https://www.google.com/search?q={google}")
        ]]
        k = await message.reply_text(text=script.I_CUDNT.format(search), reply_markup=InlineKeyboardMarkup(button))
        await asyncio.sleep(60)
        await k.delete()
        try:
            await message.delete()
        except:
            pass
        return
    user = message.from_user.id if message.from_user else 0
    buttons = [[
        InlineKeyboardButton(text=movie.get('title'), callback_data=f"spol#{movie.movieID}#{user}")
    ]
        for movie in movies
    ]
    buttons.append(
        [InlineKeyboardButton(text="🚫 ᴄʟᴏsᴇ 🚫", callback_data='close_data')]
    )
    d = await message.reply_text(text=script.CUDNT_FND.format(message.from_user.mention), reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=message.id)
    await asyncio.sleep(60)
    await d.delete()
    try:
        await message.delete()
    except:
        pass
