======================================

Web版：タスク管理AI（スマホ対応・拡張版）

======================================

使い方：

1) pip install flask pandas scikit-learn joblib

2) python app.py

3) ブラウザで http://127.0.0.1:5000 を開く（スマホ可）

from flask import Flask, request, redirect, url_for, render_template_string import pandas as pd import os import joblib from sklearn.ensemble import RandomForestClassifier from datetime import datetime

app = Flask(name)

DATA_PATH = "tasks.csv" MODEL_PATH = "task_model.pkl"

=========================

初期化

=========================

def init_data(): if not os.path.exists(DATA_PATH): df = pd.DataFrame(columns=[ "task", "importance", "urgency", "time_required", "completed", "created_at", "completed_at", "streak" ]) df.to_csv(DATA_PATH, index=False)

=========================

ホーム

=========================

@app.route('/') def index(): df = pd.read_csv(DATA_PATH)

if not df.empty:
    df = df.sort_values(by="completed")

return render_template_string(TEMPLATE, tasks=df.to_dict(orient='records'))

=========================

タスク追加

=========================

@app.route('/add', methods=['POST']) def add(): df = pd.read_csv(DATA_PATH)

new_row = {
    "task": request.form['task'],
    "importance": int(request.form['importance']),
    "urgency": int(request.form['urgency']),
    "time_required": float(request.form['time_required']),
    "completed": 0,
    "created_at": datetime.now(),
    "completed_at": "",
    "streak": 0
}

df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df.to_csv(DATA_PATH, index=False)

return redirect(url_for('index'))

=========================

完了処理

=========================

@app.route('/complete/int:idx') def complete(idx): df = pd.read_csv(DATA_PATH)

df.at[idx, 'completed'] = 1
df.at[idx, 'completed_at'] = datetime.now()
df.at[idx, 'streak'] += 1

df.to_csv(DATA_PATH, index=False)

return redirect(url_for('index'))

=========================

AI学習

=========================

@app.route('/train') def train(): df = pd.read_csv(DATA_PATH) df = df[df['completed'] == 1]

if len(df) < 5:
    return "データ不足"

X = df[["importance", "urgency", "time_required"]]
y = df["completed"]

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, MODEL_PATH)

return redirect(url_for('index'))

=========================

タスク提案

=========================

@app.route('/suggest') def suggest(): df = pd.read_csv(DATA_PATH) df = df[df['completed'] == 0]

if df.empty:
    return "タスクなし"

if not os.path.exists(MODEL_PATH):
    df['score'] = df['importance'] * df['urgency']
    top = df.sort_values('score', ascending=False).head(1)
    return f"おすすめ: {top.iloc[0]['task']}"

model = joblib.load(MODEL_PATH)
X = df[["importance", "urgency", "time_required"]]
probs = model.predict_proba(X)[:,1]

df['priority'] = probs
top = df.sort_values('priority', ascending=False).head(1)

return f"おすすめ: {top.iloc[0]['task']}"

=========================

進捗分析

=========================

@app.route('/progress') def progress(): df = pd.read_csv(DATA_PATH)

if len(df) == 0:
    return "タスクなし"

rate = df['completed'].sum() / len(df)

return f"進捗率: {rate*100:.1f}%"

=========================

HTML（スマホ対応）

=========================

TEMPLATE = """ <!doctype html>

<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: sans-serif; padding: 10px; }
input, button { margin: 5px; padding: 8px; width: 100%; }
.task { border: 1px solid #ccc; margin: 5px; padding: 10px; border-radius: 8px; }
</style>
</head>
<body>
<h2>タスクAI</h2><form method="POST" action="/add">
<input name="task" placeholder="タスク名" required>
<input name="importance" placeholder="重要度(1-5)" required>
<input name="urgency" placeholder="緊急度(1-5)" required>
<input name="time_required" placeholder="時間" required>
<button type="submit">追加</button>
</form><a href="/suggest"><button>次にやること</button></a> <a href="/train"><button>AI学習</button></a> <a href="/progress"><button>進捗</button></a>

<hr>{% for t in tasks %}

<div class="task">
<b>{{t.task}}</b><br>
重要度: {{t.importance}} / 緊急度: {{t.urgency}}<br>
{% if t.completed == 0 %}
<a href="/complete/{{loop.index0}}"><button>完了</button></a>
{% else %}
完了済み
{% endif %}
</div>
{% endfor %}</body>
</html>
"""if name == 'main': init_data() app.run(host='0.0.0.0', port=5000)
