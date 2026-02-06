import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, ChannelInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from info import ADMINS, VIDEO_CHANNEL
from database.users_db import db  
from utils import temp, get_progress_bar, get_readable_time

lock = asyncio.Lock()
INDEX_CACHE = {}

# =================================================
# 📥 COMMAND HANDLER (/index)
# =================================================
@Client.on_message(filters.command("index") & filters.private & filters.incoming & filters.user(ADMINS))
async def send_for_index(bot, message):
    if lock.locked():
        return await message.reply("⚠️ Wait until previous process completes.")

    # Step 1: Ask for last message
    prompt = await message.reply("Forward last message from channel OR send last message link.")
    try:
        msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
    except Exception as e:
        return await message.reply(f"Listener Error: {e}")
    await prompt.delete()

    # Step 2: Parse channel info
    last_msg_id, chat_id = 0, None
    if msg.text and msg.text.startswith("https://t.me"):
        try:
            parts = msg.text.split("/")
            last_msg_id = int(parts[-1])
            chat_id_str = parts[-2]
            chat_id = int(f"-100{chat_id_str}") if chat_id_str.isdigit() else chat_id_str
        except Exception:
            return await message.reply("❌ Invalid message link!")
    elif msg.forward_from_chat and msg.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = msg.forward_from_message_id
        chat_id = msg.forward_from_chat.id
    else:
        return await message.reply("❌ This is not a forwarded message or valid link.")

    try:
        chat = await bot.get_chat(chat_id)
        if chat.type != enums.ChatType.CHANNEL:
            return await message.reply("I can index only channels.")
    except Exception as e:
        return await message.reply(f"Error: {e}")

    # Step 3: Ask for skip number
    skip_prompt = await message.reply("Send skip message number (e.g., 0).")
    try:
        msg = await bot.listen(chat_id=message.chat.id, user_id=message.from_user.id)
        skip = int(msg.text)
    except Exception:
        await skip_prompt.delete()
        return await message.reply("❌ Invalid Number.")
    await skip_prompt.delete()

    # Step 4: Cache data
    INDEX_CACHE[message.from_user.id] = {
        "chat": chat.id,
        "lst_msg_id": last_msg_id,
        "skip": skip
    }

    # Step 5: Confirmation buttons
    buttons = [
        [InlineKeyboardButton("YES", callback_data="index#yes")],
        [InlineKeyboardButton("CLOSE", callback_data="index#cancel")]
    ]
    await message.reply(
        f"Do you want to index <b>{chat.title}</b>?\n\n"
        f"🆔 ID: <code>{chat.id}</code>\n"
        f"📨 Total Messages: <code>{last_msg_id}</code>\n"
        f"⏭ Skip: <code>{skip}</code>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =================================================
# 📥 CALLBACK QUERY HANDLER
# =================================================
@Client.on_callback_query(filters.regex(r"^index"))
async def index_files(bot, query):
    action = query.data.split("#")[1]  # yes, start_main, start_brazzers, cancel
    user_id = query.from_user.id

    # Cancel
    if action == "cancel":
        temp.CANCEL = True
        INDEX_CACHE.pop(user_id, None)
        return await query.message.edit("🛑 Indexing Cancelled.")

    # Check cache
    if user_id not in INDEX_CACHE:
        await query.answer("⚠️ Session Expired. Please use /index again.", show_alert=True)
        return await query.message.delete()

    data = INDEX_CACHE[user_id]
    chat, lst_msg_id, skip = data["chat"], data["lst_msg_id"], data["skip"]

    # YES → show choice menu
    if action == "yes":
        buttons = [
            [
                InlineKeyboardButton("🎬 Video Index", callback_data="index#start_main"),
                InlineKeyboardButton("🔞 Brazzers Index", callback_data="index#start_brazzers")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="index#cancel")]
        ]
        return await query.message.edit(
            "<b>📂 Select Database to Save Files:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # Start indexing
    if action.startswith("start_"):
        target_db = action.replace("start_", "")  # "main" or "brazzers"
        db_name = "Brazzers" if target_db == "brazzers" else "Main Video"
        await query.message.edit(f"<b>🚀 {db_name} Indexing started...</b>")
        await index_files_to_db(lst_msg_id, chat, query.message, bot, skip, target_db)
        INDEX_CACHE.pop(user_id, None)

# =================================================
# ⚙️ MAIN INDEXING LOGIC
# =================================================
async def index_files_to_db(lst_msg_id, chat, msg, bot, skip, target_db):
    start_time = time.time()
    total_files = duplicate = errors = deleted = no_media = unsupported = 0
    current = skip + 1
    BATCH_SIZE = 20

    async with lock:
        try:
            temp.CANCEL = False
            while current <= lst_msg_id:
                if temp.CANCEL:
                    time_taken = get_readable_time(time.time() - start_time)
                    return await msg.edit(
                        f"🛑 Indexing Cancelled!\n⏱ Time: {time_taken}\n✅ Saved: {total_files}"
                    )

                end_id = min(current + BATCH_SIZE, lst_msg_id + 1)
                ids = list(range(current, end_id))

                try:
                    messages = await bot.get_messages(chat, ids)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    messages = await bot.get_messages(chat, ids)
                except Exception:
                    errors += len(ids)
                    current += BATCH_SIZE
                    continue

                for message in messages:
                    if temp.CANCEL:
                        break
                    try:
                        if not message or message.empty:
                            deleted += 1
                            continue
                        if not message.media:
                            no_media += 1
                            continue
                        if message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
                            unsupported += 1
                            continue

                        media = getattr(message, message.media.value, None)
                        if not media:
                            unsupported += 1
                            continue

                        file_id, file_unique_id = media.file_id, media.file_unique_id
                        if target_db == "brazzers":
                            is_new = await db.add_brazzers_video(file_unique_id, file_id) or True
                        else:
                            is_new = await db.add_video(file_unique_id, file_id)

                        if is_new:
                            total_files += 1
                        else:
                            duplicate += 1
                    except Exception as e:
                        print(f"Error: {e}")
                        errors += 1

                current += BATCH_SIZE
                percentage = (min(current, lst_msg_id) / lst_msg_id) * 100
                prog_bar = get_progress_bar(percentage)
                elapsed_time = get_readable_time(time.time() - start_time)
                db_label = "🔞 Brazzers" if target_db == "brazzers" else "🎬 Video"

                btn = [[InlineKeyboardButton("CANCEL", callback_data="index#cancel")]]
                try:
                    await msg.edit(
                        f"📊 <b>{db_label} Indexing Progress</b>\n"
                        f"{prog_bar} {percentage:.1f}%\n"
                        f"━━━━━━━━━━━━━━━━\n"
                        f"📥 Scanned: <code>{min(current, lst_msg_id)}/{lst_msg_id}</code>\n"
                        f"✅ Saved: <code>{total_files}</code>\n"
                        f"♻️ Duplicates: <code>{duplicate}</code>\n"
                        f"🗑 Deleted/Skip: <code>{deleted + no_media + unsupported}</code>\n"
                        f"⚠️ Errors: <code>{errors}</code>\n"
                        f"⏱ Elapsed: <code>{elapsed_time}</code>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)

            # Final summary
            time_taken = get_readable_time(time.time() - start_time)
            db_label = "🔞 Brazzers" if target_db == "brazzers" else "🎬 Video"
            await msg.edit(f"❌ Critical Error: {e}")
    
