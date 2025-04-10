from flask import Flask, request, jsonify, render_template
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
DATA_FILE = "static/chart.png"

# 秘密のトークン（実際には環境変数や別の方法で管理するのがベター）
SECRET_TOKEN = "seikakusindan0607"  # GASと合わせたトークンを入れます

@app.route('/')
def index():
    return render_template('index.html', image_url=DATA_FILE)

@app.route('/update', methods=['POST'])
def update_chart():
    # 認証チェック
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 403

    # データの取得
    data = request.json['data']

    # 評価項目と数値を取り出す（例）
    labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
              'ストレス耐性', '独立性', '協調性', '創造性', '感受性']
    values = list(map(int, data[3:13]))  # 2列目〜11列目が数値だと仮定

    # グラフを作成
    angles = [n / float(len(labels)) * 2 * 3.14159 for n in range(len(labels))]
    values += values[:1]
    angles += angles[:1]

    plt.clf()
    plt.polar(angles, values, marker='o')
    plt.fill(angles, values, alpha=0.25)
    plt.xticks(angles[:-1], labels)

    os.makedirs("static", exist_ok=True)
    plt.savefig(DATA_FILE)

    return jsonify({"status": "success"})
