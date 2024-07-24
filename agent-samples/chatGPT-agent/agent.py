import os
from openai import OpenAI

class Agent:
    def __init__(self):
       # self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_key = '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'
        self.client = OpenAI(api_key=self.openai_api_key)

    def transform_text(self, original_text, target_style):
        prompt = f"""
        Transform the following text into the {target_style} style:

        Original text:
        {original_text}

        Transformed text ({target_style} style):
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a skilled writer capable of transforming text into various styles and tones."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    def execute(self, input_data):
        original_text = input_data.get("text", "")
        target_style = input_data.get("style", "formal")

        if not original_text:
            return {"error": "No text provided for transformation"}

        transformed_text = self.transform_text(original_text, target_style)

        return {
            "original_text": original_text,
            "target_style": target_style,
            "transformed_text": transformed_text
        }

# For local testing
if __name__ == "__main__":
    agent = Agent()
    result = agent.execute({
        "text": "Hey there! What's up? I've got some awesome news to share with you guys.",
        "style": "formal business email"
    })
    print(f"Original: {result['original_text']}")
    print(f"\nStyle: {result['target_style']}")
    print(f"\nTransformed: {result['transformed_text']}")