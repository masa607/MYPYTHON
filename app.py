from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import os
import math
import uuid

# Google Drive関連
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)

labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
          'ストレス耐性', '独立性', '協調性', '創造性', '感受性']

# Google DriveにアップロードするフォルダID（共有設定済み）
DRIVE_FOLDER_ID = 'あなたのDriveフォルダID'

# サービスアカウントキー（JSON）を使って認証
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build('drive', 'v3', credentials=credentials)


def create_radar_chart(scores, filename='chart.png'):
    num_vars = len(labels)
    angles = [n / float(num_vars) * 2 * math.pi for n in range(num_vars)]

    # グラフを閉じるために先頭を末尾に追加
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


def upload_to_drive(local_path):
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

    # 画像を公開設定にする
    drive_service.permissions().create(
        fileId=uploaded['id'],
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    file_id = uploaded['id']
    return f"https://drive.google.com/uc?id={file_id}"


latest_drive_url = None  # 画像URLを保存しておく


@app.route('/')
def index():
    global latest_drive_url
    return render_template('index.html', image_url=latest_drive_url or '')


@app.route('/update', methods=['POST'])
def update():
    global latest_drive_url
    try:
        data = request.json.get("row")
        if not data or len(data) < 13:
            return {"error": "不十分なデータが送信されました。"}

        scores = list(map(int, data[3:13]))
        chart_path = 'chart.png'
        create_radar_chart(scores, filename=chart_path)

        latest_drive_url = upload_to_drive(chart_path)

        return {"status": "success", "url": latest_drive_url}
    except Exception as e:
        return {"error": str(e)}
