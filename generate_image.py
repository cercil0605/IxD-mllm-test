import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
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

    genai.configure(api_key=api_key)

    prompt_text = convert_json_to_prompt(instructions_json)
    print(f"Generated Prompt: {prompt_text}")

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-preview-image-generation",  # 画像生成に対応
        generation_config=GenerationConfig(
            temperature=0.7
        )
    )

    try:
        base_image = Image.open(base_image_path)

        response = model.generate_content([
            {"text": prompt_text},
            base_image
        ])

        if not response.candidates:
            raise ValueError("No candidates in response.")

        parts = response.candidates[0].content.parts
        generated_image_path = "image/output.png"
        image_saved = False

        for part in parts:
            if hasattr(part, "text") and part.text:
                print("Text output:", part.text)
            if hasattr(part, "image") and part.image:
                part.image.save(generated_image_path)
                image_saved = True
                print(f"Saved to {generated_image_path}")

        if not image_saved:
            raise ValueError("No image found in response.")

    except GoogleAPIError as e:
        print(f"API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
