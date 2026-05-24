from flask import Flask, request
import requests
import os
import json
import datetime

app = Flask(__name__)

TOKEN = "8694144409:AAHVYe7R-sYMNuYE6rClFLe7j25Bh0GYrM8"
ADMIN_ID = 918596151
KANAL = "@kinochi_uzzb"
KANALCHA = "@kinochi_uzzb"
BOT = "cinemauzzb_bot"
BASE = "/home/Akbarjon20261/mysite"

# PythonAnywhere bepul tarif uchun proxy
PROXIES = {
    "http": "http://proxy.server:3128",
    "https": "http://proxy.server:3128",
}

def api(method, data={}):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/{method}",
            data=data,
            timeout=15,
            proxies=PROXIES
        )
        return r.json()
    except:
        return {}

def rd(path):
    try:
        with open(f"{BASE}/{path}", "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""

def wr(path, content, mode="w"):
    try:
        full = f"{BASE}/{path}"
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, mode, encoding="utf-8") as f:
            f.write(str(content))
    except Exception as e:
        print(f"WR ERROR: {e}")

def mkd(path):
    try:
        os.makedirs(f"{BASE}/{path}", exist_ok=True)
    except:
        pass

def rm(path):
    try:
        os.remove(f"{BASE}/{path}")
    except:
        pass

def init():
    mkd("step")
    mkd("kino")
    mkd("tizim")
    mkd("users")
    mkd("admin")
    if not rd("kino/kodi.txt"): wr("kino/kodi.txt", "0")
    if not rd("kino/son.txt"): wr("kino/son.txt", "0")
    if not rd("holat.txt"): wr("holat.txt", "Yoqilgan")
    if not rd("channel.txt"): wr("channel.txt", "@kinochi_uzzb")
    if not rd("channel2.txt"): wr("channel2.txt", "")
    if not rd("kino_ch.txt"): wr("kino_ch.txt", "@kinochi_uzzb")
    if not rd("azo.dat"): wr("azo.dat", "")
    if not rd("tizim/admins.txt"): wr("tizim/admins.txt", "")

def get_admins():
    admins = [ADMIN_ID]
    for a in rd("tizim/admins.txt").split("\n"):
        try:
            if a.strip():
                admins.append(int(a.strip()))
        except:
            pass
    return admins

def joinchat(uid):
    try:
        r = api("getChatMember", {
            "chat_id": KANAL,
            "user_id": uid
        })
        status = r.get("result", {}).get("status", "")
        return status in ["member", "administrator", "creator"]
    except:
        return False

def addstat(uid):
    path = f"users/{uid}.txt"
    if not rd(path):
        wr(path, datetime.datetime.now().strftime("%d.%m.%Y"))

def panel_kb():
    return json.dumps({
        "resize_keyboard": True,
        "keyboard": [
            [{"text": "📢 Kanallar"}, {"text": "📥 Kino Yuklash"}],
            [{"text": "✉️ Xabarnoma"}, {"text": "📊 Statistika"}],
            [{"text": "🤖 Bot holati"}, {"text": "👥 Adminlar"}],
            [{"text": "🎬 Kinolar soni"}, {"text": "🗑 Kino o'chirish"}],
            [{"text": "◀️ Orqaga"}]
        ]
    })

def bosh_kb():
    return json.dumps({
        "resize_keyboard": True,
        "keyboard": [[{"text": "◀️ Orqaga"}]]
    })

def main_kb(uid, admins):
    kb = [
        [{"text": "🔎 Kino qidirish"}, {"text": "📢 Kanal"}]
    ]
    if uid in admins:
        kb.append([{"text": "🗄 Boshqaruv paneli"}])
    return json.dumps({"resize_keyboard": True, "keyboard": kb})

def send_video_to_user(cid, kod):
    nomi = rd(f"kino/{kod}/nomi.txt")
    video_id = rd(f"kino/{kod}/film.txt")
    downcount = rd(f"kino/{kod}/downcount.txt") or "0"
    if video_id:
        wr(f"kino/{kod}/downcount.txt", int(downcount) + 1)
        api("sendVideo", {
            "chat_id": cid,
            "video": video_id,
            "caption": (
                f"<b>🍿 Kino haqida:\n"
                f"<blockquote>{nomi}</blockquote>\n\n"
                f"🔰 Kanal: @kinochi_uzzb\n"
                f"🗂 Yuklashlar: {downcount}\n\n"
                f"🤖 Bot: @{BOT}</b>"
            ),
            "parse_mode": "html",
            "reply_markup": json.dumps({"inline_keyboard": [
                [{"text": "🔎 Kino kodlari", "url": "https://t.me/kinochi_uzzb"}],
                [{"text": "📋 Ulashish", "url": f"https://t.me/share/url?url=https://t.me/{BOT}?start={kod}"}]
            ]})
        })
        return True
    return False

try:
    init()
except:
    pass


def main(data):
    try:
        msg = data.get("message", {}) or {}
        cb = data.get("callback_query", {}) or {}
        admins = get_admins()

        if msg:
            cid = msg.get("chat", {}).get("id")
            uid = msg.get("from", {}).get("id")
            name = msg.get("from", {}).get("first_name", "") or ""
            familya = msg.get("from", {}).get("last_name", "") or ""
            nameru = f"<a href='tg://user?id={uid}'>{name} {familya}</a>"
            text = msg.get("text", "") or ""
            caption = msg.get("caption", "") or ""
            video = msg.get("video")
            photo = msg.get("photo")
            mid = msg.get("message_id")
            step = rd(f"step/{cid}.step")
            holat = rd("holat.txt")
            kanalcha = rd("kino_ch.txt")
            now = datetime.datetime.now().strftime("%d.%m.%Y | %H:%M")

            addstat(uid)

            baza = rd("azo.dat")
            if str(cid) not in baza:
                wr("azo.dat", f"\n{cid}", "a")
                api("sendMessage", {
                    "chat_id": ADMIN_ID,
                    "text": (
                        f"<b>👤 Yangi foydalanuvchi!\n\n"
                        f"👤 Ism: {name} {familya}\n"
                        f"🆔 ID: <code>{cid}</code>\n"
                        f"🕒 Vaqt: {now}</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "👀 Ko'rish", "url": f"tg://user?id={cid}"}]
                    ]})
                })

            if holat == "O'chirilgan" and uid not in admins:
                api("sendMessage", {
                    "chat_id": cid,
                    "text": "⛔️ <b>Bot vaqtinchalik o'chirilgan!</b>",
                    "parse_mode": "html"
                })
                return "ok"

            if text == "/start" or (text.startswith("/start ") and len(text.split()) > 1):
                parts = text.split(" ")
                kod = parts[1] if len(parts) > 1 else ""

                if not joinchat(uid):
                    if kod:
                        wr(f"step/{cid}.kino_ids", kod)
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": f"<b>⚠️ Salom {name}!\n\nBotdan foydalanish uchun kanalga obuna bo'ling!</b>",
                        "parse_mode": "html",
                        "reply_markup": json.dumps({"inline_keyboard": [
                            [{"text": "📢 Kanalga obuna bo'lish", "url": "https://t.me/kinochi_uzzb"}],
                            [{"text": "🔄 Obunani tekshirish", "callback_data": "checksuv"}]
                        ]})
                    })
                    return "ok"

                if kod:
                    if not send_video_to_user(cid, kod):
                        api("sendMessage", {
                            "chat_id": cid,
                            "text": "❌ <b>Film topilmadi!</b>",
                            "parse_mode": "html"
                        })
                    return "ok"

                api("sendMessage", {
                    "chat_id": cid,
                    "text": (
                        f"🖐 <b>Assalomu alaykum, {nameru}!\n\n"
                        f"<blockquote>🎬 Kino kodini yuboring!\n"
                        f"📢 Kanal: @kinochi_uzzb</blockquote>\n\n"
                        f"🔎 Kino kodini yuboring:</b>"
                    ),
                    "parse_mode": "html",
                    "disable_web_page_preview": True,
                    "reply_markup": main_kb(uid, admins)
                })
                return "ok"

            if text == "◀️ Orqaga":
                rm(f"step/{cid}.step")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"🖐 <b>Assalomu alaykum, {nameru}!\n\n🔎 Kino kodini yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": main_kb(uid, admins)
                })
                return "ok"

            if text in ["🗄 Boshqaruv paneli", "/panel"] and uid in admins:
                rm(f"step/{cid}.step")
                total = rd("azo.dat").count("\n")
                kino_son = rd("kino/son.txt") or "0"
                api("sendMessage", {
                    "chat_id": cid,
                    "text": (
                        f"<b>🗄 Admin paneliga xush kelibsiz!\n\n"
                        f"📊 Foydalanuvchilar: {total} ta\n"
                        f"🎬 Kinolar: {kino_son} ta\n"
                        f"⏰ {now}</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if text == "🎬 Kinolar soni" and uid in admins:
                kino_son = rd("kino/son.txt") or "0"
                kod = rd("kino/kodi.txt") or "0"
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>🎬 Kinolar:\n\n📦 Jami: {kino_son} ta\n🔢 So'nggi kod: {kod}</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if text == "🗑 Kino o'chirish" and uid in admins:
                wr(f"step/{cid}.step", "delete_kino")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": "<b>🗑 O'chirilishi kerak bo'lgan kino kodini yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                return "ok"

            if step == "delete_kino" and uid in admins:
                if text.isdigit():
                    if rd(f"kino/{text}/film.txt"):
                        rm(f"kino/{text}/film.txt")
                        rm(f"kino/{text}/nomi.txt")
                        rm(f"kino/{text}/rasm.txt")
                        rm(f"kino/{text}/downcount.txt")
                        son = max(0, int(rd("kino/son.txt") or 1) - 1)
                        wr("kino/son.txt", son)
                        rm(f"step/{cid}.step")
                        api("sendMessage", {
                            "chat_id": cid,
                            "text": f"<b>✅ {text} kodli kino o'chirildi!</b>",
                            "parse_mode": "html",
                            "reply_markup": panel_kb()
                        })
                    else:
                        api("sendMessage", {
                            "chat_id": cid,
                            "text": "❌ <b>Bunday kino topilmadi!</b>",
                            "parse_mode": "html"
                        })
                return "ok"

            if text == "📥 Kino Yuklash" and uid in admins:
                api("sendMessage", {
                    "chat_id": cid,
                    "text": "<b>⁉️ Kino yuklash usulini tanlang:</b>",
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "✅ Rasm + Video", "callback_data": "oddiyk"}],
                        [{"text": "❌ Bekor", "callback_data": "bekor"}]
                    ]})
                })
                return "ok"

            if step == "rasm" and photo and uid in admins:
                k = rd("step/new_kino.txt")
                mkd(f"kino/{k}")
                photo_id = photo[-1]["file_id"]
                wr(f"kino/{k}/rasm.txt", photo_id)
                wr(f"step/{cid}.step", "kinoo")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": "<b>✅ Rasm saqlandi!\n\nEndi filmni caption bilan yuboring!\n\n<i>⚠️ Caption majburiy!</i></b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                return "ok"

            if step == "kinoo" and video and uid in admins:
                if not caption:
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": "⚠️ <b>Filmni caption (tavsif) bilan yuboring!</b>",
                        "parse_mode": "html"
                    })
                    return "ok"
                kod = rd("kino/kodi.txt")
                mkd(f"kino/{kod}")
                wr(f"kino/{kod}/nomi.txt", caption)
                wr(f"kino/{kod}/film.txt", video["file_id"])
                wr(f"kino/{kod}/downcount.txt", "0")
                rasm = rd(f"kino/{kod}/rasm.txt")
                api("sendPhoto", {
                    "chat_id": kanalcha,
                    "photo": rasm,
                    "caption": (
                        f"<b>🍿 Yangi film!\n\n"
                        f"<blockquote>{caption}</blockquote>\n\n"
                        f"🔢 Kod: <code>{kod}</code>\n\n"
                        f"📥 Bot: @{BOT}</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "📥 Yuklab olish", "url": f"https://t.me/{BOT}?start={kod}"}]
                    ]})
                })
                son = int(rd("kino/son.txt") or 0)
                wr("kino/son.txt", son + 1)
                rm(f"step/{cid}.step")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✅ Film joylandi!\n\n🔢 Kod: <code>{kod}</code>\n🎬 Jami: {son+1} ta</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if step == "sendpost" and uid in admins:
                rm(f"step/{cid}.step")
                users = [u for u in rd("azo.dat").split("\n") if u.strip()]
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>⏳ {len(users)} ta foydalanuvchiga yuborilmoqda...</b>",
                    "parse_mode": "html"
                })
                x = y = 0
                for u in users:
                    r = api("copyMessage", {
                        "from_chat_id": cid,
                        "chat_id": u.strip(),
                        "message_id": mid
                    })
                    if r.get("ok"): x += 1
                    else: y += 1
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✅ Tayyor!\n\n📨 Jami: {len(users)}\n✅ Yuborildi: {x}\n❌ Yuborilmadi: {y}</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if step == "sendfwrd" and uid in admins:
                rm(f"step/{cid}.step")
                users = [u for u in rd("azo.dat").split("\n") if u.strip()]
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>⏳ {len(users)} ta foydalanuvchiga yuborilmoqda...</b>",
                    "parse_mode": "html"
                })
                x = y = 0
                for u in users:
                    r = api("forwardMessage", {
                        "from_chat_id": cid,
                        "chat_id": u.strip(),
                        "message_id": mid
                    })
                    if r.get("ok"): x += 1
                    else: y += 1
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✅ Tayyor!\n\n📨 Jami: {len(users)}\n✅ Yuborildi: {x}\n❌ Yuborilmadi: {y}</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if step == "add_admin" and uid == ADMIN_ID:
                try:
                    new_id = int(text.strip())
                    current = rd("tizim/admins.txt")
                    if str(new_id) not in current:
                        wr("tizim/admins.txt", f"{new_id}\n", "a")
                        api("sendMessage", {
                            "chat_id": new_id,
                            "text": "<b>🎉 Siz admin qildingiz!</b>",
                            "parse_mode": "html"
                        })
                    rm(f"step/{cid}.step")
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": f"<b>✅ <code>{new_id}</code> admin qilindi!</b>",
                        "parse_mode": "html",
                        "reply_markup": panel_kb()
                    })
                except:
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": "❌ <b>Faqat ID raqam yuboring!</b>",
                        "parse_mode": "html"
                    })
                return "ok"

            if step == "remove_admin" and uid == ADMIN_ID:
                current = rd("tizim/admins.txt")
                new = "\n".join([a for a in current.split("\n") if a.strip() and a.strip() != text.strip()])
                wr("tizim/admins.txt", new)
                rm(f"step/{cid}.step")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✅ <code>{text.strip()}</code> admin ro'yxatidan o'chirildi!</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if step == "add_channel" and uid in admins:
                if text.startswith("@") or text.startswith("-100"):
                    current = rd("channel.txt")
                    if text not in current:
                        wr("channel.txt", f"{current}\n{text}" if current else text)
                    rm(f"step/{cid}.step")
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": f"<b>✅ {text} kanali qo'shildi!</b>",
                        "parse_mode": "html",
                        "reply_markup": panel_kb()
                    })
                else:
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": "❌ <b>@ bilan yuboring!\nMasalan: @kinochi_uzzb yoki -100 ID</b>",
                        "parse_mode": "html"
                    })
                return "ok"

            if step == "remove_channel" and uid in admins:
                current = rd("channel.txt")
                new = "\n".join([c for c in current.split("\n") if c.strip() and c.strip() != text.strip()])
                wr("channel.txt", new)
                rm(f"step/{cid}.step")
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✅ {text.strip()} kanali o'chirildi!</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })
                return "ok"

            if text == "📊 Statistika" and uid in admins:
                stat = rd("azo.dat").count("\n")
                bugun = datetime.datetime.now().strftime("%d.%m.%Y")
                users_dir = f"{BASE}/users"
                bugungi = 0
                if os.path.exists(users_dir):
                    for f in os.listdir(users_dir):
                        if rd(f"users/{f}") == bugun:
                            bugungi += 1
                api("sendMessage", {
                    "chat_id": cid,
                    "text": (
                        f"<b>📊 Bot statistikasi:\n\n"
                        f"👥 Jami: {stat} ta\n"
                        f"📅 Bugun yangilar: {bugungi} ta\n"
                        f"🎬 Kinolar: {rd('kino/son.txt') or 0} ta\n"
                        f"⏰ {now}</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [[
                        {"text": "📅 Kunlik", "callback_data": "kunlik"},
                        {"text": "📆 Haftalik", "callback_data": "haftalik"},
                        {"text": "📊 Oylik", "callback_data": "oylik"}
                    ]]})
                })
                return "ok"

            if text == "✉️ Xabarnoma" and uid in admins:
                users = [u for u in rd("azo.dat").split("\n") if u.strip()]
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>✉️ Xabarnoma\n\n👥 Foydalanuvchilar: {len(users)} ta</b>",
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "💠 Oddiy", "callback_data": "send"},
                         {"text": "💠 Forward", "callback_data": "send2"}],
                        [{"text": "❌ Bekor", "callback_data": "bekor"}]
                    ]})
                })
                return "ok"

            if text == "🤖 Bot holati" and uid in admins:
                holat = rd("holat.txt")
                xolat = "❌ O'chirish" if holat == "Yoqilgan" else "✅ Yoqish"
                emoji = "✅" if holat == "Yoqilgan" else "❌"
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>🤖 Bot holati: {emoji} {holat}</b>",
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": xolat, "callback_data": "bot_holat"}]
                    ]})
                })
                return "ok"

            if text == "👥 Adminlar" and uid in admins:
                admins_list = rd("tizim/admins.txt")
                msg_text = f"<b>👥 Adminlar:\n\n🔰 Bosh admin: <code>{ADMIN_ID}</code>"
                if admins_list:
                    for a in admins_list.split("\n"):
                        if a.strip():
                            msg_text += f"\n👤 <code>{a.strip()}</code>"
                msg_text += "</b>"
                kb = [[{"text": "➕ Admin qo'shish", "callback_data": "add_admin"}]]
                if uid == ADMIN_ID:
                    kb.append([{"text": "🗑 Admin o'chirish", "callback_data": "remove_admin"}])
                kb.append([{"text": "🔙 Orqaga", "callback_data": "boshqar"}])
                api("sendMessage", {
                    "chat_id": cid,
                    "text": msg_text,
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": kb})
                })
                return "ok"

            if text == "📢 Kanallar" and uid in admins:
                kanallar = rd("channel.txt")
                xabar_matni = kanallar or "Hali kanal qo'shilmagan"
                api("sendMessage", {
                    "chat_id": cid,
                    "text": f"<b>📢 Majburiy kanallar:\n\n{xabar_matni}</b>",
                    "parse_mode": "html",
                    "reply_markup": json.dumps({
                        "inline_keyboard": [
                            [{"text": "➕ Qo'shish", "callback_data": "add_channel"}],
                            [{"text": "🗑 O'chirish", "callback_data": "remove_channel"}],
                            [{"text": "⬅️ Orqaga", "callback_data": "boshqar"}]
                        ]
                    })
                })
                return "ok"

            if text.isdigit() and not step:
                if not joinchat(uid):
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": "<b>⚠️ Botdan foydalanish uchun kanalga obuna bo'ling!</b>",
                        "parse_mode": "html",
                        "reply_markup": json.dumps({"inline_keyboard": [
                            [{"text": "📢 Obuna bo'lish", "url": "https://t.me/kinochi_uzzb"}],
                            [{"text": "🔄 Tekshirish", "callback_data": "checksuv"}]
                        ]})
                    })
                    return "ok"
                if not send_video_to_user(cid, text):
                    api("sendMessage", {
                        "chat_id": cid,
                        "text": "❌ <b>Bunday kodli film topilmadi!\n\nKodni tekshiring!</b>",
                        "parse_mode": "html"
                    })
                return "ok"

        if cb:
            cid2 = cb.get("message", {}).get("chat", {}).get("id")
            mid2 = cb.get("message", {}).get("message_id")
            uid2 = cb.get("from", {}).get("id")
            data2 = cb.get("data", "")
            admins = get_admins()
            holat = rd("holat.txt")
            now = datetime.datetime.now().strftime("%d.%m.%Y | %H:%M")

            api("answerCallbackQuery", {"callback_query_id": cb["id"]})

            if data2 == "checksuv":
                if joinchat(uid2):
                    api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                    api("sendMessage", {
                        "chat_id": cid2,
                        "text": "<b>✅ Obunangiz tasdiqlandi!\n\n🔎 Kino kodini yuboring:</b>",
                        "parse_mode": "html",
                        "reply_markup": main_kb(uid2, admins)
                    })
                    saved = rd(f"step/{cid2}.kino_ids")
                    if saved:
                        rm(f"step/{cid2}.kino_ids")
                        send_video_to_user(cid2, saved)
                else:
                    api("answerCallbackQuery", {
                        "callback_query_id": cb["id"],
                        "text": "❌ Hali obuna bo'lmadingiz!",
                        "show_alert": True
                    })

            elif data2 in ["boshqar", "bosh"] and uid2 in admins:
                total = rd("azo.dat").count("\n")
                kino_son = rd("kino/son.txt") or "0"
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": (
                        f"<b>🗄 Admin paneli\n\n"
                        f"👥 Foydalanuvchilar: {total} ta\n"
                        f"🎬 Kinolar: {kino_son} ta\n"
                        f"⏰ {now}</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })

            elif data2 == "oddiyk" and uid2 in admins:
                kod = int(rd("kino/kodi.txt") or 0) + 1
                wr("kino/kodi.txt", kod)
                wr("step/new_kino.txt", kod)
                mkd(f"kino/{kod}")
                wr(f"step/{cid2}.step", "rasm")
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": f"<b>📸 Kino rasmi yuboring!\n\n🔢 Yangi kod: <code>{kod}</code></b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })

            elif data2 == "bekor":
                rm(f"step/{cid2}.step")
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": "<b>Bekor qilindi.</b>",
                    "parse_mode": "html",
                    "reply_markup": panel_kb()
                })

            elif data2 == "send" and uid2 in admins:
                users = [u for u in rd("azo.dat").split("\n") if u.strip()]
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": f"<b>📝 {len(users)} ta foydalanuvchiga xabar yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "sendpost")

            elif data2 == "send2" and uid2 in admins:
                users = [u for u in rd("azo.dat").split("\n") if u.strip()]
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": f"<b>📝 {len(users)} ta foydalanuvchiga forward xabar yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "sendfwrd")

            elif data2 == "bot_holat" and uid2 in admins:
                holat = rd("holat.txt")
                wr("holat.txt", "O'chirilgan" if holat == "Yoqilgan" else "Yoqilgan")
                new_holat = rd("holat.txt")
                emoji = "✅" if new_holat == "Yoqilgan" else "❌"
                api("editMessageText", {
                    "chat_id": cid2,
                    "message_id": mid2,
                    "text": f"<b>🤖 Bot holati: {emoji} {new_holat}</b>",
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 Orqaga", "callback_data": "boshqar"}]
                    ]})
                })

            elif data2 == "add_admin" and uid2 == ADMIN_ID:
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": "<b>👤 Yangi admin ID raqamini yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "add_admin")

            elif data2 == "remove_admin" and uid2 == ADMIN_ID:
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": "<b>🗑 O'chiriladigan admin ID raqamini yuboring:</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "remove_admin")

            elif data2 == "add_channel" and uid2 in admins:
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": "<b>📢 Kanal username yuboring:\n\nMasalan: @kinochi_uzzb</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "add_channel")

            elif data2 == "remove_channel" and uid2 in admins:
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})
                api("sendMessage", {
                    "chat_id": cid2,
                    "text": "<b>📢 O'chiriladigan kanal username yuboring:\n\nMasalan: @kinochi_uzzb</b>",
                    "parse_mode": "html",
                    "reply_markup": bosh_kb()
                })
                wr(f"step/{cid2}.step", "remove_channel")

            elif data2 == "stat" and uid2 in admins:
                stat = rd("azo.dat").count("\n")
                api("editMessageText", {
                    "chat_id": cid2,
                    "message_id": mid2,
                    "text": (
                        f"<b>📊 Statistika\n\n"
                        f"✅ Jami: {stat} ta\n"
                        f"🎬 Kinolar: {rd('kino/son.txt') or 0} ta</b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [[
                        {"text": "📅 Kunlik", "callback_data": "kunlik"},
                        {"text": "📆 Haftalik", "callback_data": "haftalik"},
                        {"text": "📊 Oylik", "callback_data": "oylik"}
                    ]]})
                })

            elif data2 == "kunlik" and uid2 in admins:
                users_dir = f"{BASE}/users"
                counts = {}
                today = datetime.datetime.now()
                for i in range(5):
                    d = (today - datetime.timedelta(i)).strftime("%d.%m.%Y")
                    counts[d] = 0
                if os.path.exists(users_dir):
                    for f in os.listdir(users_dir):
                        s = rd(f"users/{f}")
                        if s in counts:
                            counts[s] += 1
                days = list(counts.items())
                labels = ["Bugun", "Kecha", "2 kun oldin", "3 kun oldin", "4 kun oldin"]
                text_msg = "<b>📅 Kunlik statistika:\n\n<blockquote>"
                for i, (d, c) in enumerate(days):
                    text_msg += f"🔹 {labels[i]}: {c} ta\n"
                text_msg += "</blockquote></b>"
                api("editMessageText", {
                    "chat_id": cid2, "message_id": mid2,
                    "text": text_msg, "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 Orqaga", "callback_data": "stat"}]
                    ]})
                })

            elif data2 == "haftalik" and uid2 in admins:
                users_dir = f"{BASE}/users"
                hafta = {}
                if os.path.exists(users_dir):
                    for f in os.listdir(users_dir):
                        s = rd(f"users/{f}")
                        try:
                            d = datetime.datetime.strptime(s, "%d.%m.%Y")
                            w = d.strftime("%W-%Y")
                            hafta[w] = hafta.get(w, 0) + 1
                        except:
                            pass
                now_w = datetime.datetime.now().strftime("%W-%Y")
                last_w = (datetime.datetime.now() - datetime.timedelta(7)).strftime("%W-%Y")
                last2_w = (datetime.datetime.now() - datetime.timedelta(14)).strftime("%W-%Y")
                api("editMessageText", {
                    "chat_id": cid2, "message_id": mid2,
                    "text": (
                        f"<b>📆 Haftalik:\n\n<blockquote>"
                        f"🔹 Bu hafta: {hafta.get(now_w,0)} ta\n"
                        f"🔹 O'tgan hafta: {hafta.get(last_w,0)} ta\n"
                        f"🔹 2 hafta oldin: {hafta.get(last2_w,0)} ta"
                        f"</blockquote></b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 Orqaga", "callback_data": "stat"}]
                    ]})
                })

            elif data2 == "oylik" and uid2 in admins:
                users_dir = f"{BASE}/users"
                oylar = {}
                if os.path.exists(users_dir):
                    for f in os.listdir(users_dir):
                        s = rd(f"users/{f}")
                        try:
                            d = datetime.datetime.strptime(s, "%d.%m.%Y")
                            m = d.strftime("%m.%Y")
                            oylar[m] = oylar.get(m, 0) + 1
                        except:
                            pass
                now_m = datetime.datetime.now().strftime("%m.%Y")
                last_m = (datetime.datetime.now().replace(day=1) - datetime.timedelta(1)).strftime("%m.%Y")
                last2_m = (datetime.datetime.now().replace(day=1) - datetime.timedelta(32)).strftime("%m.%Y")
                api("editMessageText", {
                    "chat_id": cid2, "message_id": mid2,
                    "text": (
                        f"<b>📊 Oylik:\n\n<blockquote>"
                        f"🔹 Bu oy: {oylar.get(now_m,0)} ta\n"
                        f"🔹 O'tgan oy: {oylar.get(last_m,0)} ta\n"
                        f"🔹 2 oy oldin: {oylar.get(last2_m,0)} ta"
                        f"</blockquote></b>"
                    ),
                    "parse_mode": "html",
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": "🔙 Orqaga", "callback_data": "stat"}]
                    ]})
                })

            elif data2 == "yopish":
                api("deleteMessage", {"chat_id": cid2, "message_id": mid2})

    except Exception as e:
        print(f"ERROR: {e}")


@app.route("/", methods=["GET"])
def index():
    return "✅ Bot ishlayapti!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.json
        if not data:
            return "ok"
        main(data)
        return "OK"
    except Exception as e:
        print(f"WEBHOOK ERROR: {e}")
        return "OK"
