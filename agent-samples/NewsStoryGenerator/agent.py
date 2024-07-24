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

    def generate_news_snippet(self, topic, key_points, tone):
        prompt = f"""
        Create an engaging news snippet about {topic}. 
        Include these key points: {', '.join(key_points)}
        The tone should be {tone}.
        
        The snippet should be around 150 words and include:
        1. An attention-grabbing headline
        2. A concise summary of the news
        3. A quote from a relevant source (you can create a fictional source if needed)
        4. A brief conclusion or future outlook

        End with a vivid description of a key visual element from the story, prefixed with 'KEY VISUAL:'.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled journalist who creates engaging and informative news snippets."},
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
                    "text": scene_description + ", photorealistic news image",
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
        temp_image_path = "/tmp/news_image.png"
        image.save(temp_image_path)

        return temp_image_path

    def execute(self, input_data):
        topic = input_data.get("topic", "Recent technological advancements")
        key_points = input_data.get("key_points", ["Innovation", "Impact on society", "Future prospects"])
        tone = input_data.get("tone", "informative yet engaging")

        # Generate the news snippet
        news_content = self.generate_news_snippet(topic, key_points, tone)

        # Extract the key visual description
        content_parts = news_content.split("KEY VISUAL:")
        main_content = content_parts[0].strip()
        visual_description = content_parts[1].strip() if len(content_parts) > 1 else "A relevant image for " + topic

        # Generate the image
        image_path = self.generate_image(visual_description)

        # Extract the headline
        headline = main_content.split("\n")[0].strip()
        body = "\n".join(main_content.split("\n")[1:]).strip()

        return {
            "headline": headline,
            "body": body,
            "key_visual_description": visual_description,
            "image_path": image_path
        }

# For local testing
if __name__ == "__main__":
    agent = Agent()
    result = agent.execute({
        "topic": "The impact of artificial intelligence on job markets",
        "key_points": ["Automation trends", "New job creation", "Skills for the future"],
        "tone": "balanced and thought-provoking"
    })
    print(f"Headline: {result['headline']}")
    print(f"\nBody:\n{result['body']}")
    print(f"\nKey Visual: {result['key_visual_description']}")
    print(f"\nImage saved at: {result['image_path']}")