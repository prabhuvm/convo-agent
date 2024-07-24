import os
import openai
import requests
from PIL import Image
from io import BytesIO
import base64

class Agent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")

        openai.api_key = self.openai_api_key

    def generate_story(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative storyteller. Write a short, engaging story of about 150 words based on the given prompt. End with a vivid description of a key scene from the story, prefixed with 'KEY SCENE:'."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']

    def generate_image(self, scene_description):
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

        body = {
            "steps": 40,
            "width": 1024,
            "height": 1024,
            "seed": 0,
            "cfg_scale": 5,
            "samples": 1,
            "text_prompts": [
                {
                    "text": scene_description,
                    "weight": 1
                }
            ],
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.stability_api_key}",
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        image_base64 = data["artifacts"][0]["base64"]
        image = Image.open(BytesIO(base64.b64decode(image_base64)))

        # Save image to a temporary file
        temp_image_path = "/tmp/generated_image.png"
        image.save(temp_image_path)

        return temp_image_path

    def execute(self, input_data):
        story_prompt = input_data.get("prompt", "A mysterious adventure in a magical forest")

        # Generate the story
        story = self.generate_story(story_prompt)

        # Extract the key scene description
        story_parts = story.split("KEY SCENE:")
        main_story = story_parts[0].strip()
        scene_description = story_parts[1].strip() if len(story_parts) > 1 else main_story

        # Generate the image
        image_path = self.generate_image(scene_description)

        return {
            "story": main_story,
            "key_scene": scene_description,
            "image_path": image_path
        }

# For local testing
if __name__ == "__main__":
    agent = Agent()
    result = agent.execute({"prompt": "A time-traveling detective solving a mystery in ancient Egypt"})
    print(result["story"])
    print("\nKey Scene:")
    print(result["key_scene"])
    print(f"\nImage saved at: {result['image_path']}")