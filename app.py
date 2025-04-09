from flask import Flask, request, jsonify
import matplotlib.pyplot as plt
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

app = Flask(__name__)
DATA_FILE = "static/chart.png"
SPREADSHEET_ID = "1EBau2fDErE932IRHreuk_9p8Gcc67ugoPXD10a5TV9o"
SHEET_NAME = "フォームの回答1"  # 例: "Sheet1"など
SECRET_TOKEN = "AIzaSyCb_dq9YidZZKBcdxDEm5yVmMtBCoe3usk"

# Google Sheets API認証
def get_google_sheets_service():
    creds, project = google.auth.load_credentials_from_file('path_to_your_service_account_json.json')
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

@app.route('/update', methods=['POST'])
def update_chart():
    # 認証チェック
    token = request.headers.get('Authorization')
    if not token or token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 403

    # データの取得と処理
    data = request.json['data']
    labels = ['外向性', '計画性', '柔軟性', '論理的思考', '直感的思考',
              'ストレス耐性', '独立性', '協調性', '創造性', '感受性']
    values = list(map(int, data[3:13]))

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

    # Google Sheetsに画像のURLを更新
    image_url = f"https://yourdomain.com/{DATA_FILE}"  # RenderなどでホストしているURLに置き換えてください

    try:
        service = get_google_sheets_service()
        range_ = f"{SHEET_NAME}!A15"  # 15行目に画像のURLを設定
        values = [[image_url]]  # 15行目にURLを設定
        body = {
            'values': values
        }
        # スプレッドシートを更新
        service.update(spreadsheetId=SPREADSHEET_ID, range=range_, valueInputOption="RAW", body=body).execute()
    except HttpError as err:
        print(f"Error updating Google Sheets: {err}")

    return jsonify({"status": "success"})
