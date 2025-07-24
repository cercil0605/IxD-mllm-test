import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# 1. .envからAPIキーを読み込む
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEYが設定されていません。.envファイルを確認してください。")

genai.configure(api_key=API_KEY)

# 2. 入力画像を読み込む
base_image = Image.open('image/img2.png')

# 3. JSON形式の整理整頓指示を読み込んでテキストプロンプトに変換
with open('instructions.json', 'r', encoding='utf-8') as f:
    instructions = json.load(f)

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
        prompt = f"部屋を整理整頓してください。具体的には、{instructions_text}。"
    else:
        prompt = f"部屋を整理整頓してください: {data}"
    return prompt

prompt_text = convert_json_to_prompt(instructions)
print("Generated prompt:", prompt_text)

# 4. Geminiモデル呼び出し
model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")

try:
    response = model.generate_content([prompt_text, base_image])
except Exception as e:
    print("Gemini API呼び出し中にエラーが発生しました:", e)
    exit(1)

# 5. レスポンスから画像データを保存
generated_image_path = "image/output.png"
image_saved = False

for part in response.parts:
    if hasattr(part, "text") and part.text:
        print("Model text output:", part.text)
    if hasattr(part, "data") and part.data:
        output_img = Image.open(BytesIO(part.data))
        output_img.save(generated_image_path)
        image_saved = True
        print(f"Generated image saved to {generated_image_path}")

if not image_saved:
    print("生成された画像が取得できませんでした。プロンプトを調整してください。")
