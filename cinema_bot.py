import requests
import os
import json
import datetime
import time
import threading

# ==================== SETUP ====================
TOKEN = "8694144409:AAHVYe7R-sYMNuYE6rClFLe7j25Bh0GYrM8"
ADMIN_ID = 918596151
BASE_DIR = "/tmp"

# ==================== HELPER FUNCTIONS ====================
def api(method, data=None):
    """Telegram API ga so'rov yuborish"""
    try:
        if data is None:
            data = {}
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/{method}",
            data=data,
            timeout=15
        )
        return r.json()
    except Exception as e:
        print(f"API ERROR: {e}")
        return {"ok": False}

def send_message(cid, text, parse_mode="HTML", reply_markup=None):
    """Xabar yuborish"""
    data = {
        "chat_id": cid,
        "text": text,
        "parse_mode": parse_mode
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    return api("sendMessage", data)

def send_photo(cid, photo_id, caption="", parse_mode="HTML"):
    """Rasm yuborish"""
    data = {
        "chat_id": cid,
        "photo": photo_id,
        "caption": caption,
        "parse_mode": parse_mode
    }
    return api("sendPhoto", data)

def send_video(cid, video_id, caption="", parse_mode="HTML"):
    """Video yuborish"""
    data = {
        "chat_id": cid,
        "video": video_id,
        "caption": caption,
        "parse_mode": parse_mode
    }
    return api("sendVideo", data)

def answer_callback(callback_id, text="", show_alert=False):
    """Callback answer"""
    data = {
        "callback_query_id": callback_id,
        "text": text,
        "show_alert": show_alert
    }
    return api("answerCallbackQuery", data)

# ==================== FILE STORAGE ====================
def get_data(key, default=None):
    """Fayldan data o'qish"""
    try:
        path = f"{BASE_DIR}/{key}.json"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default if default is not None else {}

def save_data(key, data):
    """Faylga data saqlash"""
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        path = f"{BASE_DIR}/{key}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"SAVE ERROR: {e}")
        return False

def get_movies():
    return get_data("movies", {})

def save_movies(movies):
    return save_data("movies", movies)

def get_users():
    return get_data("users", {})

def save_users(users):
    return save_data("users", users)

def get_admins():
    admins = get_data("admins", {})
    if str(ADMIN_ID) not in admins:
        admins[str(ADMIN_ID)] = {"name": "Asosiy Admin"}
        save_data("admins", admins)
    return admins

# ==================== BOT COMMANDS ====================
def cmd_start(cid, uid, name):
    """START komandasi"""
    users = get_users()
    if str(uid) not in users:
        users[str(uid)] = {
            "name": name,
            "joined": datetime.datetime.now().isoformat(),
            "films_watched": 0
        }
        save_users(users)
    
    text = f"""
<b>🎬 Xush kelibsiz, {name}!</b>

<b>CinemaBot</b> ga xush kelibsiz! 🎥

Bu yerdan siz:
✅ Yangi filmlarni topishingiz mumkin
✅ Kinolarni qidirish
✅ Statistikalarni ko'rish

Quyidagi tugmalardan foydalaning:
"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔍 Qidirish", "callback_data": "search"}],
            [{"text": "📊 Statistika", "callback_data": "stats"}],
            [{"text": "ℹ️ Ma'lumot", "callback_data": "info"}]
        ]
    }
    send_message(cid, text, reply_markup=keyboard)

def cmd_admin(cid, uid):
    """Admin panel"""
    admins = get_admins()
    if str(uid) not in admins:
        send_message(cid, "❌ Siz admin emassiz!")
        return
    
    users = get_users()
    movies = get_movies()
    
    total_views = sum(m.get("views", 0) for m in movies.values())
    
    top_movies = sorted(
        [(m.get("name", "Nomaxush"), m.get("views", 0)) for m in movies.values()],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    top_text = ""
    if top_movies:
        top_text = "\n\n<b>🏆 Eng ko'p ko'rilgan (Top 3):</b>\n"
        for i, (name, views) in enumerate(top_movies, 1):
            top_text += f"  {i}. {name} - <b>{views}</b> ▶️\n"
    
    text = f"""
<b>👨‍💼 ADMIN PANEL</b>

📊 <b>Statistika:</b>
  • Foydalanuvchilar: <b>{len(users)}</b> 👥
  • Jami filmlar: <b>{len(movies)}</b> 🎬
  • Jami ko'rishlar: <b>{total_views}</b> ▶️{top_text}

<b>Admin operatsiyalari:</b>
"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "➕ Film qo'shish", "callback_data": "add_movie"}],
            [{"text": "📈 Film statistikasi", "callback_data": "all_stats"}],
            [{"text": "📢 Xabar yuborish", "callback_data": "broadcast"}],
            [{"text": "🗑 Film o'chirish", "callback_data": "delete_movie"}],
            [{"text": "👥 Userlar", "callback_data": "users_list"}],
            [{"text": "🔙 Orqaga", "callback_data": "back_menu"}]
        ]
    }
    send_message(cid, text, reply_markup=keyboard)

def cmd_all_stats(cid, uid):
    """Barcha film statistikasi"""
    admins = get_admins()
    if str(uid) not in admins:
        send_message(cid, "❌ Siz admin emassiz!")
        return
    
    movies = get_movies()
    
    if not movies:
        send_message(cid, "📽 Hali film qo'shilmagan!")
        return
    
    sorted_movies = sorted(
        movies.items(),
        key=lambda x: x[1].get("views", 0),
        reverse=True
    )
    
    text = "<b>📈 FILM STATISTIKASI</b>\n\n"
    total_views = 0
    
    for i, (movie_id, movie) in enumerate(sorted_movies, 1):
        name = movie.get("name", "Nomaxush")
        views = movie.get("views", 0)
        text += f"{i}. <b>{name}</b> - {views} ▶️\n"
        total_views += views
    
    text += f"\n<b>Jami ko'rishlar:</b> {total_views}"
    
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Admin Panel", "callback_data": "admin_menu"}]
        ]
    }
    send_message(cid, text, reply_markup=keyboard)

def cmd_stats(cid, uid):
    """Foydalanuvchi statistikasi"""
    users = get_users()
    movies = get_movies()
    user_data = users.get(str(uid), {})
    
    total_views = sum(m.get("views", 0) for m in movies.values())
    
    text = f"""
<b>📊 STATISTIKA</b>

👤 <b>Sizning ma'lumotlaringiz:</b>
  • Ism: <b>{user_data.get('name', 'Noma\'lum')}</b>
  • ID: <b>{uid}</b>
  • Qo'shilgan: <b>{user_data.get('joined', 'Noma\'lum')[:10]}</b>

📈 <b>Umumiy ma'lumot:</b>
  • Foydalanuvchilar: <b>{len(users)}</b>
  • Jami filmlar: <b>{len(movies)}</b>
  • Jami ko'rishlar: <b>{total_views}</b>
"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "🔙 Orqaga", "callback_data": "back_menu"}]
        ]
    }
    send_message(cid, text, reply_markup=keyboard)

# ==================== MAIN MESSAGE HANDLER ====================
def handle_message(cid, uid, fname, text):
    """Xabar qayta ishlash"""
    if text.startswith("/start"):
        cmd_start(cid, uid, fname)
    elif text.startswith("/admin"):
        cmd_admin(cid, uid)
    elif text.startswith("/"):
        send_message(cid, "❌ Noma'lum komanda!")
    else:
        # Qidirish
        movies = get_movies()
        found = []
        for movie_id, movie in movies.items():
            if text.lower() in movie.get("name", "").lower():
                found.append((movie_id, movie))
        
        if found:
            for movie_id, movie in found[:5]:
                # Ko'rish sonini oshir
                movie["views"] = movie.get("views", 0) + 1
                movies[movie_id] = movie
                save_movies(movies)
                
                caption = f"""
<b>{movie.get('name', 'Nomaxush')}</b>

<b>Tavsifi:</b> {movie.get('description', 'Yo\'q')}

<b>Janr:</b> {movie.get('genre', 'Noma\'lum')}
<b>Yil:</b> {movie.get('year', 'Noma\'lum')}
<b>Ko'rishlar:</b> {movie.get('views', 0)} ▶️
"""
                if movie.get("video_id"):
                    send_video(cid, movie.get("video_id"), caption)
                elif movie.get("photo_id"):
                    send_photo(cid, movie.get("photo_id"), caption)
        else:
            send_message(cid, f"❌ '{text}' topilmadi!")

def handle_callback(cid, uid, data_cb, callback_id):
    """Callback query qayta ishlash"""
    if data_cb == "search":
        send_message(cid, "🔍 <b>Qidirish</b>\n\nFilm nomini yozing:")
    elif data_cb == "stats":
        cmd_stats(cid, uid)
    elif data_cb == "info":
        send_message(cid, "<b>ℹ️ CinemaBot Haqida</b>\n\nBu bot eng yangi va mashhur kinolarni qidiruv uchun! 🎬")
    elif data_cb == "admin_menu":
        cmd_admin(cid, uid)
    elif data_cb == "all_stats":
        cmd_all_stats(cid, uid)
    elif data_cb == "back_menu":
        users = get_users()
        user = users.get(str(uid), {})
        cmd_start(cid, uid, user.get("name", "User"))
    
    answer_callback(callback_id, "✅")

# ==================== POLLING LOOP ====================
def polling_loop():
    """Telegram updates ni polling qilish"""
    offset = 0
    print("🚀 Bot polling rejimida ishga tushdi...")
    
    while True:
        try:
            updates = api("getUpdates", {"offset": offset, "timeout": 30})
            
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update.get("update_id") + 1
                    
                    # TEXT MESSAGE
                    msg = update.get("message", {})
                    if msg:
                        cid = msg.get("chat", {}).get("id")
                        uid = msg.get("from", {}).get("id")
                        fname = msg.get("from", {}).get("first_name", "User")
                        text = msg.get("text", "").strip()
                        
                        print(f"📨 Message: {uid} - {text}")
                        handle_message(cid, uid, fname, text)
                    
                    # CALLBACK QUERY
                    cb = update.get("callback_query", {})
                    if cb:
                        cid = cb.get("from", {}).get("id")
                        uid = cb.get("from", {}).get("id")
                        data_cb = cb.get("data", "")
                        callback_id = cb.get("id", "")
                        
                        print(f"🔘 Callback: {uid} - {data_cb}")
                        handle_callback(cid, uid, data_cb, callback_id)
        
        except Exception as e:
            print(f"❌ Polling Error: {e}")
            time.sleep(5)

# ==================== MAIN ====================
if __name__ == "__main__":
    polling_loop()
