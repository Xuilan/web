from flask import Flask, request, jsonify
from telethon import TelegramClient
import json
import os

app = Flask(__name__)

# Путь к базе данных
DATABASE_FILE = "database.json"

# Инициализация базы данных
if not os.path.exists(DATABASE_FILE):
    with open(DATABASE_FILE, "w") as f:
        json.dump({}, f)

def load_database():
    with open(DATABASE_FILE, "r") as f:
        return json.load(f)

def save_database(data):
    with open(DATABASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Авторизация Telethon клиента
@app.route('/api/auth', methods=['POST'])
def auth():
    data = request.json
    phone = data['phone']
    app_id = data['app_id']
    api_hash = data['api_hash']

    client = TelegramClient(phone, int(app_id), api_hash)

    try:
        client.connect()
        if not client.is_user_authorized():
            code_hash = client.send_code_request(phone)
            return jsonify({"status": "code_sent", "phone_code_hash": code_hash.phone_code_hash})
        return jsonify({"status": "already_authorized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        client.disconnect()

# Проверка кода подтверждения
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    phone = data['phone']
    code = data['code']
    app_id = data['app_id']
    api_hash = data['api_hash']
    phone_code_hash = data['phone_code_hash']

    client = TelegramClient(phone, int(app_id), api_hash)

    try:
        client.connect()
        client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        return jsonify({"status": "authorized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        client.disconnect()

# Сохранение параметров рассылки
@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    data = request.json
    user_id = data['user_id']

    db = load_database()
    db[user_id] = data
    save_database(db)

    return jsonify({"status": "success"})

# Запуск Flask
if __name__ == "__main__":
    app.run(port=5000)