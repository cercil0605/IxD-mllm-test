import json
from analyze_room import analyze_room_condition
from generate_image import generate_cleaned_image

def main():
    """
    Main function to run the room analysis and image generation process.
    """
    image_to_analyze = 'image/img2.png'
    prompt_for_analysis = 'prompt/get_score_and_solve.txt'
    analysis_output_path = 'analysis_result.json'
    generated_image_path = 'image/after_image.png'

    # 1. Analyze the room condition
    print("Step 1: Analyzing room condition...")
    analysis_result = analyze_room_condition(image_to_analyze, prompt_for_analysis)

    if not analysis_result:
        print("Failed to analyze room. Exiting.")
        return

    # 2. Save the analysis result to a JSON file
    print(f"Step 2: Saving analysis result to {analysis_output_path}...")
    with open(analysis_output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=4)
    print("Analysis result saved.")

    # 3. Generate the cleaned image based on the analysis
    print("Step 3: Generating cleaned image...")
    cleaned_image = generate_cleaned_image(image_to_analyze, analysis_result)

    if not cleaned_image:
        print("Failed to generate image. Exiting.")
        return
    
    print("Finished: Done Generated cleaned Image and Score,Json")

if __name__ == "__main__":
    main()