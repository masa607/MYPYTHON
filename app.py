from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import os
import math
import uuid

app = Flask(__name__)

labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
          'ストレス耐性', '独立性', '協調性', '創造性', '感受性']

latest_image_filename = None  # 最新画像ファイル名を保存

def create_radar_chart(scores, filename):
    print("[INFO] レーダーチャート作成中...")
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]

    scores += [scores[0]]
    angles += [angles[0]]

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, marker='o')
    ax.fill(angles, scores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    plt.savefig(filename, bbox_inches='tight')
    plt.close()
    print("[INFO] レーダーチャート保存完了:", filename)


@app.route('/')
def index():
    global latest_image_filename
    print("[INFO] indexアクセス - 最新画像ファイル名:", latest_image_filename)
    return render_template('index.html', image_url=f'/static/{latest_image_filename}' if latest_image_filename else '')


@app.route('/update', methods=['POST'])
def update():
    global latest_image_filename
    try:
        data = request.json.get("row")
        print("[DEBUG] 受信データ:", data)

        if not data or len(data) < 13:
            print("[ERROR] データが不十分です")
            return {"error": "不十分なデータが送信されました。"}

        scores = list(map(int, data[3:13]))
        print("[INFO] スコアデータ:", scores)

        # 画像保存先（static/に保存）
        filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        chart_path = os.path.join('static', filename)
        create_radar_chart(scores, filename=chart_path)

        latest_image_filename = filename

        return {"status": "success", "url": f"/static/{filename}"}
    except Exception as e:
        print("[ERROR] update処理でエラー:", str(e))
        return {"error": str(e)}

