import os
import json
import base64
import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# 1. .envからAPIキーを読み込む
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEYが設定されていません。.envファイルを確認してください。")

# 2. 入力画像を読み込む
base_image = Image.open('image/img2.png')

# 3. Goサーバーから直接JSONを取得
GO_SERVER_URL = 'http://localhost:8080/'  
response = requests.get(GO_SERVER_URL)
if response.status_code == 200:
    instructions = response.json()
else:
    raise Exception(f"Goサーバーへのリクエストに失敗しました。ステータスコード: {response.status_code}")

# JSONをプロンプトテキストに変換する関数
def convert_json_to_prompt(data):
    if isinstance(data, dict) and "tasks" in data:
        task_descs = []
        for task in data["tasks"]:
            action = task.get("action")
            item = task.get("item", "")
            if action == "move":
                src = task.get("from", "")
                dst = task.get("to", "")
                task_descs.append(f"{src}にある{item}を{dst}に移動する")
            elif action in ("store", "put_away", "organize"):
                loc = task.get("location", "")
                task_descs.append(f"{item}を{loc}に片付ける")
        instructions_text = "、".join(task_descs)
        prompt = (
            "この画像は、散らかった部屋Aの画像です。"
            "あなたはこの部屋Aを綺麗にする必要があります。"
            "私がこれから言う指示をよく読んで内容を整理し、優先度の高い順に処理を実施して、"
            "部屋Aを整理整頓した後の状態の画像を生成してください。指示は下記の通りです。:"
            f"{instructions_text}以上です。"
        )
    else:
        prompt = (
            "この画像は、散らかった部屋Aの画像です。"
            "あなたはこの部屋Aを綺麗にする必要があります。"
            "私がこれから言う指示をよく読んで内容を整理し、優先度の高い順に処理を実施して、"
            "部屋Aを整理整頓した後の状態の画像を生成してください。指示は下記の通りです。:"
            f"{data}以上です。"
        )
    return prompt

prompt_text = convert_json_to_prompt(instructions)
print("Generated prompt:", prompt_text)

# 4. Geminiモデル呼び出し（APIエンドポイントへの直接リクエスト）
# 画像をBase64エンコードし、APIリクエスト用のペイロードを作成
buffer = BytesIO()
base_image.save(buffer, format="PNG")
image_bytes = buffer.getvalue()
image_base64 = base64.b64encode(image_bytes).decode('utf-8')
mime_type = "image/png"

payload = {
    "contents": [
        {
            "parts": [
                { "text": prompt_text },
                { 
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_base64
                    }
                }
            ]
        }
    ],
    "generationConfig": {
        "responseModalities": ["IMAGE", "TEXT"]  # テキストと画像の両方を応答として要求する必要あり
    }
}


url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={API_KEY}"
headers = { 'Content-Type': 'application/json' }
response = requests.post(url, headers=headers, data=json.dumps(payload))
response_json = response.json()

# APIエラーをチェック
if 'error' in response_json:
    err_msg = response_json['error'].get('message', '(詳細不明)')
    raise Exception(f"Gemini API エラー: {err_msg}")

# 5. レスポンスから画像データを取得して保存・表示
generated_image_path = "image/output.png"
image_saved = False

# 応答の候補からpartsを取得（最初の候補を想定）
parts = response_json.get('candidates', [{}])[0].get('content', {}).get('parts', [])
for part in parts:
    # テキストパートがあればコンソール出力
    if part.get("text"):
        print("Model text output:", part["text"])
    # 画像データパートがあれば保存して表示
    if part.get("inlineData"):
        # Base64データをデコードして画像化
        image_data = base64.b64decode(part["inlineData"]["data"])
        output_img = Image.open(BytesIO(image_data))
        output_img.save(generated_image_path)
        image_saved = True
        print(f"Generated image saved to {generated_image_path}")
        try:
            output_img.show()  # UI上で画像を表示する（環境によっては画像ビューアが起動します）
        except Exception as e:
            print("画像の自動表示に失敗しました:", e)

if not image_saved:
    print("生成された画像を取得できませんでした。プロンプトや設定を調整してください。")
