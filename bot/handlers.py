"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Bot Handlers

 Version : 0.1
===========================================================
"""

from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

from bot import api_client
from bot.config import ALLOWED_USER_IDS
from bot.formatting import now_playing_keyboard, now_playing_text

MAX_RESULTS_PER_KIND = 8


def restricted(handler):
    @wraps(handler)
    async def wrapper(update, context):
        user = update.effective_user

        if not user or user.id not in ALLOWED_USER_IDS:
            if update.message:
                await update.message.reply_text("Доступ запрещён.")
            elif update.callback_query:
                await update.callback_query.answer("Доступ запрещён.", show_alert=True)
            return

        return await handler(update, context)

    return wrapper


async def _send_now_playing(message, state=None):
    if state is None:
        state = api_client.get_state()

    await message.reply_text(
        now_playing_text(state),
        reply_markup=now_playing_keyboard(state),
        parse_mode="HTML",
    )


@restricted
async def start(update, context):
    await update.message.reply_text(
        "MusicCenter бот. Команды:\n"
        "/now — сейчас играет\n"
        "/search <запрос> — найти и запустить музыку"
    )
    await _send_now_playing(update.message)


@restricted
async def now_playing(update, context):
    await _send_now_playing(update.message)


@restricted
async def search(update, context):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Использование: /search <запрос>")
        return

    data = api_client.search(query)

    if not data or not data.get("success"):
        await update.message.reply_text("Ошибка поиска — сервер недоступен.")
        return

    results = data.get("results", {})
    buttons = []

    for album in results.get("albums", [])[:MAX_RESULTS_PER_KIND]:
        label = f"💿 {album.get('name', '?')} — {album.get('artist', '')}"
        buttons.append([InlineKeyboardButton(label[:64], callback_data=f"pa:{album['id']}")])

    for song in results.get("songs", [])[:MAX_RESULTS_PER_KIND]:
        label = f"🎵 {song.get('title', '?')} — {song.get('artist', '')}"
        buttons.append([InlineKeyboardButton(label[:64], callback_data=f"pt:{song['id']}")])

    if not buttons:
        await update.message.reply_text(f"По запросу «{query}» ничего не найдено.")
        return

    await update.message.reply_text(
        f"Результаты по «{query}»:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@restricted
async def button_callback(update, context):
    query = update.callback_query
    data = query.data

    if data == "toggle":
        result = api_client.toggle()
    elif data == "next":
        result = api_client.next_track()
    elif data == "prev":
        result = api_client.previous_track()
    elif data == "refresh":
        result = {"success": True, "state": api_client.get_state()}
    elif data in ("vol_up", "vol_down"):
        state = api_client.get_state() or {}
        current = state.get("volume", 70)
        delta = 10 if data == "vol_up" else -10
        result = api_client.set_volume(max(0, min(100, current + delta)))
    elif data.startswith("pa:"):
        result = api_client.play({"kind": "album", "id": data[3:]})
    elif data.startswith("pt:"):
        result = api_client.play({"kind": "track", "id": data[3:]})
    else:
        await query.answer()
        return

    if not result or not result.get("success"):
        await query.answer("Не удалось выполнить команду", show_alert=True)
        return

    await query.answer()
    state = result.get("state") or api_client.get_state()

    if data.startswith("pa:") or data.startswith("pt:"):
        # Playing from a search-results list: post a fresh now-playing
        # card instead of overwriting the results.
        await _send_now_playing(query.message, state)
        return

    try:
        await query.edit_message_text(
            now_playing_text(state),
            reply_markup=now_playing_keyboard(state),
            parse_mode="HTML",
        )
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise
