from flask import Flask, render_template, request, redirect
import subprocess
import os
import threading
import requests
import time
from platform import system

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# === HTML PANEL ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    for file_key in ['token', 'convo', 'file', 'hatersname', 'time', 'password']:
        file = request.files.get(file_key)
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{file_key}.txt"))
    return redirect('/')

@app.route('/run-script')
def run_script():
    threading.Thread(target=send_messages).start()
    return 'Script is now running in the background.'

# === MESSAGE SENDER ===
def send_messages():
    with open('uploads/password.txt', 'r') as file:
        password = file.read().strip()

    entered_password = password  # Removed input prompt for automation

    if entered_password != password:
        print('[-] Incorrect Password!')
        return

    with open('uploads/token.txt', 'r') as file:
        tokens = file.readlines()
    num_tokens = len(tokens)

    requests.packages.urllib3.disable_warnings()

    def cls():
        if system() == 'Linux':
            os.system('clear')
        elif system() == 'Windows':
            os.system('cls')

    cls()

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'referer': 'www.google.com'
    }

    access_tokens = [token.strip() for token in tokens]

    with open('uploads/convo.txt', 'r') as file:
        convo_id = file.read().strip()

    with open('uploads/file.txt', 'r') as file:
        text_file_path = file.read().strip()

    with open(text_file_path, 'r') as file:
        messages = file.readlines()

    num_messages = len(messages)
    max_tokens = min(num_tokens, num_messages)

    with open('uploads/hatersname.txt', 'r') as file:
        haters_name = file.read().strip()

    with open('uploads/time.txt', 'r') as file:
        speed = int(file.read().strip())

    while True:
        try:
            for message_index in range(num_messages):
                token_index = message_index % max_tokens
                access_token = access_tokens[token_index]
                message = messages[message_index].strip()
                url = f"https://graph.facebook.com/v15.0/t_{convo_id}/"
                parameters = {'access_token': access_token, 'message': f"{haters_name} {message}"}
                response = requests.post(url, json=parameters, headers=headers)
                current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")
                if response.ok:
                    print(f"[+] Message {message_index + 1} sent: {haters_name} {message} at {current_time}")
                else:
                    print(f"[x] Failed to send {message_index + 1}: {haters_name} {message} at {current_time}")
                time.sleep(speed)
            print("[+] All messages sent. Restarting...")
        except Exception as e:
            print(f"[!] Error: {e}")

# === FLASK ENTRY ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
