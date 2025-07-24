import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core.exceptions import GoogleAPIError

def convert_json_to_prompt(data):
    if isinstance(data, dict) and "improvement_suggestions" in data:
        task_descs = [f"{task.get('target_area', '')}を{task.get('suggestion', '')}" for task in data["improvement_suggestions"]]
        instructions_text = "、".join(task_descs)
        return (
            "この画像は、散らかった部屋の画像です。"
            "以下の指示に従って、部屋を整理整頓した後の状態の画像を生成してください。\n"
            f"指示: {instructions_text}"
        )
    else:
        return "この画像は、散らかった部屋の画像です。画像を分析し、整理整頓してください。"

def generate_cleaned_image(base_image_path, instructions_json):
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEYが設定されていません。.envファイルを確認してください。")

    client = genai.Client(api_key=api_key)

    prompt_text = convert_json_to_prompt(instructions_json)
    print(f"Generated Prompt: {prompt_text}")

    try:
        base_image = Image.open(base_image_path)

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[prompt_text,base_image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        if not response.candidates:
            raise ValueError("No candidates in response.")

        parts = response.candidates[0].content.parts
        generated_image_path = "image/output.png"
        image_saved = False

        for part in parts:
            if hasattr(part, "text") and part.text:
                print("Text output:", part.text)
            if hasattr(part, "inline_data") and part.inline_data:
                mime_type = part.inline_data.mime_type
                if mime_type.startswith("image/"):
                    image = Image.open(BytesIO(part.inline_data.data))
                    image.save(generated_image_path)
                    print(f"Image saved to {generated_image_path}")
                    image_saved = True
                    return True
        if not image_saved:
            raise ValueError("No image found in response.")
    except GoogleAPIError as e:
        print(f"API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
