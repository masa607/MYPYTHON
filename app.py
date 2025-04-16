from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import os
import math
import uuid

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
          'ストレス耐性', '独立性', '協調性', '創造性', '感受性']

DRIVE_FOLDER_ID = '1L-M95Ce-_4UYCdcmEAO1zNoX_BmUDcRb'
SERVICE_ACCOUNT_FILE = 'neon-effect-456403-k6-2fbf3676c38a.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)

latest_drive_url = None  # 画像URLを保存


def create_radar_chart(scores, filename='chart.png'):
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


def upload_to_drive(local_path):
    print("[INFO] Google Driveにアップロード中:", local_path)
    file_metadata = {
        'name': f'chart_{uuid.uuid4().hex[:8]}.png',
        'parents': [DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(local_path, mimetype='image/png')
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    drive_service.permissions().create(
        fileId=uploaded['id'],
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    file_id = uploaded['id']
    drive_url = f"https://drive.google.com/uc?id={file_id}"
    print("[INFO] アップロード成功 URL:", drive_url)
    return drive_url


@app.route('/')
def index():
    global latest_drive_url
    print("[INFO] indexアクセス - 最新URL:", latest_drive_url)
    return render_template('index.html', image_url=latest_drive_url or '')


@app.route('/update', methods=['POST'])
def update():
    global latest_drive_url
    try:
        data = request.json.get("row")
        print("[DEBUG] 受信データ:", data)

        if not data or len(data) < 13:
            print("[ERROR] データが不十分です")
            return {"error": "不十分なデータが送信されました。"}

        scores = list(map(int, data[3:13]))
        print("[INFO] スコアデータ:", scores)

        chart_path = 'chart.png'
        create_radar_chart(scores, filename=chart_path)

        latest_drive_url = upload_to_drive(chart_path)

        return {"status": "success", "url": latest_drive_url}
    except Exception as e:
        print("[ERROR] update処理でエラー:", str(e))
        return {"error": str(e)}


        return {"status": "success", "url": latest_drive_url}
    except Exception as e:
        return {"error": str(e)}
