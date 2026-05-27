import os
import json
from flask import Flask, render_template, request, redirect, url_for, make_response

# Жестко привязываем папку templates
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

# Путь к вечной папке Amvera
DATA_FILE = '/data/users.txt'

moms_database = [
    {"id": 0, "name": "Мария", "district": "Центральный", "baby_age": 5, "interests": "ИТ, ГВ", "liked_you": True},
    {"id": 1, "name": "Анна", "district": "Центральный", "baby_age": 4, "interests": "Йога, ГВ", "liked_you": False},
    {"id": 2, "name": "Ольга", "district": "Приморский", "baby_age": 12, "interests": "Спорт, Книги", "liked_you": False},
    {"id": 3, "name": "Юлия", "district": "Центральный", "baby_age": 3, "interests": "Питон, Кофе, Фриланс", "liked_you": True}
]

current_index = 0
match_message = ""
user_profile = None

@app.route('/')
def index():
    global current_index, match_message, user_profile
    if not user_profile:
        return redirect(url_for('register'))
    if current_index >= len(moms_database):
        current_index = 0
    mom = moms_database[current_index]
    msg = match_message
    match_message = "" 
    
    response = make_response(render_template('index.html', mom=mom, match_message=msg, user=user_profile))
    # Современная защита, которая разрешает открывать сайт внутри фреймов ВК
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://vk.com https://*.vk.com https://vkmini.apps;"
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    global user_profile
    if request.method == 'POST':
        user_profile = {
            "name": request.form.get('name'),
            "district": request.form.get('district'),
            "baby_age": request.form.get('baby_age'),
            "interests": request.form.get('interests')
        }
        try:
            with open(DATA_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(user_profile, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")
            
        return redirect(url_for('index'))
        
    response = make_response(render_template('register.html'))
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://vk.com https://*.vk.com https://vkmini.apps;"
    return response

@app.route('/swipe', methods=['POST'])
def swipe():
    global current_index, match_message
    mom_id = int(request.form.get('mom_id'))
    action = request.form.get('action')
    if action == 'like':
        current_mom = moms_database[mom_id]
        if current_mom['liked_you']:
            match_message = f"Взаимный мэтч с {current_mom['name']}! Напишите ей."
    current_index += 1
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    global current_index
    current_index = 0
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
