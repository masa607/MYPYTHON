from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
import os
import math
import uuid
import requests  # ← GASに送るために追加

app = Flask(__name__)

# === 📌 日本語フォント設定 ===
font_path = os.path.join('fonts', 'ipaexg.ttf')
font_prop = None

if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    matplotlib.rcParams['font.family'] = font_prop.get_name()
    print("[INFO] 日本語フォントを設定:", font_prop.get_name())
else:
    print("⚠ fonts/ipaexg.ttf が見つかりません。日本語が文字化けする可能性があります。")

labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
          'ストレス耐性', '独立性', '協調性', '創造性', '感受性']

latest_image_filename = None

def create_radar_chart(scores, filename, font_prop=None):
    print("[INFO] レーダーチャート作成中...")
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]

    scores += [scores[0]]
    angles += [angles[0]]

    plt.clf()
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, scores, marker='o', color='blue', linewidth=2)
    ax.fill(angles, scores, alpha=0.25, color='skyblue')
    ax.set_xticks(angles[:-1])
    if font_prop:
        ax.set_xticklabels(labels, fontsize=10, fontproperties=font_prop)
    else:
        ax.set_xticklabels(labels, fontsize=10)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_ylim(0, 5)
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

        filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        chart_path = os.path.join('static', filename)

        create_radar_chart(scores, filename=chart_path, font_prop=font_prop)
        latest_image_filename = filename

        # === 🔽 GASに画像URLをPOSTする ===
        gas_webhook_url = "https://script.google.com/macros/s/AKfycbydUdatckkWzrsJDi3Eh_JkT9W4KQbENaJybxS4A5fJ2QcSrnaWLWE1me4_JaOsuj_0Uw/exec"

        # Render上などでホスティングされている本番URLに置き換えてください
        image_url = f"https://your-domain.com/static/{filename}"

        payload = {
            "image_url": image_url
        }

        try:
            res = requests.post(gas_webhook_url, json=payload)
            print("[INFO] GASへの送信結果:", res.text)
        except Exception as e:
            print("[ERROR] GAS送信失敗:", str(e))

        return {"status": "success", "url": f"/static/{filename}"}
    except Exception as e:
        print("[ERROR] update処理でエラー:", str(e))
        return {"error": str(e)}





