import requests
from openai import OpenAI
from http import HTTPStatus
import json
from config import AI_SYSTEM_ROLE


class OvayniseAI:
    def __init__(
            self,
            AI_API_KEY,
            AI_URL_API,
            AI_BALANCE_URL,
            AI_MODEL,
            AI_ROLE,
            AI_MAX_TOKENS,
            AI_HEADERS
    ):
        self.AI_API_KEY = AI_API_KEY
        self.AI_URL_API = AI_URL_API
        self.AI_BALANCE_URL = AI_BALANCE_URL
        self.AI_MODEL = AI_MODEL
        self.AI_ROLE = AI_ROLE
        self.AI_MAX_TOKENS = AI_MAX_TOKENS
        self.AI_HEADERS = AI_HEADERS

    def show_balance(self):
        try:
            response = requests.get(
                self.AI_BALANCE_URL,
                headers=self.AI_HEADERS)
            if response.status_code == HTTPStatus.OK:
                balance_info = response.json()
                return balance_info.get('balance')
            else:
                print(f"Request failed "
                      f"with status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request to balance API failed: {e}")

    def show_ai_answer(self, message):
        client = OpenAI(
            api_key=self.AI_API_KEY,
            base_url=self.AI_URL_API,
        )

        chat_completion = client.chat.completions.create(
            model=self.AI_MODEL,
            messages=[AI_SYSTEM_ROLE,
                {"role": self.AI_ROLE, "content": message}],
            max_tokens= self.AI_MAX_TOKENS
        )
        response = chat_completion.json()
        response_dict = json.loads(response)
        text = response_dict['choices'][0]['message']['content']
        return text
