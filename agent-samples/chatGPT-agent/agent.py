import os
from openai import OpenAI

class Agent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)

    def transform_text(self, original_text, target_style, prev_text):
        prompt = f"""
        You are a {target_style}. Engage in a informal conversation with a user who has asked: "{original_text}" and 
        your previous response was: {prev_text}. You can use previous response for context and continuation. 
        Respond with a mix of humor, knowledge, and empathy. Keep it informal conversation.
        Make the user feel comfortable and understood.  
        Response has tobe complete in 100 words with no incomplete sentences in the end of response."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a {target_style}. You are expert in the field."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=250,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response.choices[0].message.content.strip()


    def execute(self, input_data):
        original_text = input_data.get("text", "")
        prev_text = input_data.get("prev", "")
        target_style = input_data.get("style", "formal")

        if not original_text:
            return {"error": "No text provided for transformation"}

        transformed_text = self.transform_text(original_text, target_style, prev_text)

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
        "prev": "",
        "style": "doctor",
    })
    print(f"Original: {result['original_text']}")
    print(f"\nStyle: {result['target_style']}")
    print(f"\nTransformed: {result['transformed_text']}")