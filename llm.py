import os
import openai
import logging

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPEN_AI_KEY')

class LLM:
    def __init__(self, model: str = 'gpt-4o-mini'):
        self.model = model
        self._system_prompt = (
            "You are an expert in product improvement for mobile and web applications."
            "Your goal is to analyze user feedback—especially negative comments—and propose concrete, "
            "step-by-step solutions for improving the product. Provide your answers in a structured and "
            "professional manner. If you require additional details, ask clarifying questions."
        )

    def generate_response(self, user_prompt: str, system_prompt: str = None, **kwargs) -> str:
        requests_system_prompt = system_prompt if system_prompt else self._system_prompt

        messages = [
            {"role": "system", "content": requests_system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error: {e}")
            return ''
