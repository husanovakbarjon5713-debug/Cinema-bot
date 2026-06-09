from flask import Flask
import requests, os, json, datetime, time, threading

app = Flask(__name__)

TOKEN = "8694144409:AAHVYe7R-sYMNuYE6rClFLe7j25Bh0GYrM8"
ADMIN_ID = 918596151
BASE_DIR = "/tmp"

def api(method, data=None):
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/{method}", data=data or {}, timeout=15)
        return r.json()
    except Exception as e:
        print(f"ERROR: {e}")
        return {}

def send(cid, text, markup=None):
    data = {"chat_id": cid, "text": text, "parse_mode": "HTML"}
    if markup:
        data["reply_markup"] = json.dumps(markup)
    return api("sendMessage", data)

def answer_cb(cb_id, text=""):
    api("answerCallbackQuery", {"callback_query_id": cb_id, "text": text})

def get_data(key, default=None):
    try:
        path = f"{BASE_DIR}/{key}.json"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default or {}

def save_data(key, data):
    try:
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(f"{BASE_DIR}/{key}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"SAVE ERROR: {e}")

def handle_message(msg):
    cid = msg["chat"]["id"]
    uid = msg["from"]["id"]
    name = msg["from"].get("first_name", "User")
    text = msg.get("text", "").strip()

    users = get_data("users")
    if str(uid) not in users:
        users[str(uid)] = {"name": name, "joined": str(datetime.date.today())}
        save_data("users", users)

    print(f"MSG {uid}: {text}", flush=True)

    if text == "/start":
        kb = {"inline_keyboard": [
            [{"text": "🔍 Qidirish", "callback_data": "search"}],
            [{"text": "📊 Statistika", "callback_data": "stats"}],
        ]}
        send(cid, f"🎬 <b>Xush kelibsiz, {name}!</b>\n\nFilm kodi yoki nom yozing:", kb)

    elif text == "/admin":
        admins = get_data("admins")
        if str(ADMIN_ID) not in admins:
            admins[str(ADMIN_ID)] = {"name": "Admin"}
            save_data("admins", admins)
        if str(uid) in admins:
            movies = get_data("movies")
            users2 = get_data("users")
            total_views = sum(m.get("views", 0) for m in movies.values())
            kb = {"inline_keyboard": [
                [{"text": "➕ Film qo'shish", "callback_data": "add_movie"}],
                [{"text": "📈 Statistika", "callback_data": "all_stats"}],
                [{"text": "🗑 Film o'chirish", "callback_data": "del_movie"}],
                [{"text": "👥 Userlar", "callback_data": "users_list"}],
            ]}
            send(cid, f"👨‍💼 <b>ADMIN PANEL</b>\n\n👥 Userlar: <b>{len(users2)}</b>\n🎬 Filmlar: <b>{len(movies)}</b>\n▶️ Ko'rishlar: <b>{total_views}</b>", kb)
        else:
            send(cid, "❌ Siz admin emassiz!")
    else:
        movies = get_data("movies")
        found = [(mid, m) for mid, m in movies.items() if text.lower() in m.get("name","").lower() or text == mid]
        if found:
            for mid, m in found[:3]:
                m["views"] = m.get("views", 0) + 1
                movies[mid] = m
                save_data("movies", movies)
                send(cid, f"🎬 <b>{m.get('name','')}</b>\n\n{m.get('description','')}\n\n▶️ Ko'rishlar: {m.get('views',0)}")
        else:
            send(cid, f"❌ '<b>{text}</b>' topilmadi!")

def handle_callback(cb):
    cid = cb["from"]["id"]
    uid = cb["from"]["id"]
    data = cb.get("data", "")
    cb_id = cb["id"]
    print(f"CB {uid}: {data}", flush=True)

    if data == "search":
        send(cid, "🔍 Film nomini yozing:")
    elif data == "stats":
        users = get_data("users")
        movies = get_data("movies")
        total_views = sum(m.get("views", 0) for m in movies.values())
        send(cid, f"📊 <b>STATISTIKA</b>\n\n👥 Userlar: <b>{len(users)}</b>\n🎬 Filmlar: <b>{len(movies)}</b>\n▶️ Ko'rishlar: <b>{total_views}</b>")
    elif data == "all_stats":
        movies = get_data("movies")
        if not movies:
            send(cid, "📽 Hali film yo'q!")
        else:
            s = sorted(movies.items(), key=lambda x: x[1].get("views",0), reverse=True)
            text = "📈 <b>FILM STATISTIKASI</b>\n\n"
            for i,(mid,m) in enumerate(s,1):
                text += f"{i}. {m.get('name','?')} — {m.get('views',0)} ▶️\n"
            send(cid, text)
    elif data == "users_list":
        users = get_data("users")
        text = f"👥 <b>USERLAR</b> — {len(users)} ta\n\n"
        for uid2, u in list(users.items())[:20]:
            text += f"• {u.get('name','?')} ({uid2})\n"
        send(cid, text)

    answer_cb(cb_id)

def polling():
    offset = 0
    print("🚀 Polling boshlandi!", flush=True)
    # Eski webhookni o'chir
    api("deleteWebhook", {"drop_pending_updates": True})
    while True:
        try:
            resp = api("getUpdates", {"offset": offset, "timeout": 30})
            if resp.get("ok"):
                for upd in resp.get("result", []):
                    offset = upd["update_id"] + 1
                    if "message" in upd:
                        handle_message(upd["message"])
                    if "callback_query" in upd:
                        handle_callback(upd["callback_query"])
        except Exception as e:
            print(f"POLL ERROR: {e}", flush=True)
            time.sleep(5)

# ⚡ MODULE IMPORT BO'LGANDA START QILADI (gunicorn uchun)
print("🤖 Bot module yuklandi, polling thread ishga tushmoqda...", flush=True)
polling_thread = threading.Thread(target=polling, daemon=True)
polling_thread.start()

@app.route("/")
def index():
    return "✅ CinemaBot ishlayapti!"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Port {port}...", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

