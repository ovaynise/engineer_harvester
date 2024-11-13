from datetime import datetime, timedelta
from config import logger_bot

import requests


class TokenManager:
    def __init__(self, oauth_token, cache_duration_minutes=45):
        self.oauth_token = oauth_token
        self.iam_token = None
        self.token_expiry = datetime.now()
        self.cache_duration = timedelta(minutes=cache_duration_minutes)

    def refresh_token(self):
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        data = {"yandexPassportOauthToken": self.oauth_token}
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            token_data = response.json()
            self.iam_token = token_data.get("iamToken")
            expires_at = token_data.get("expiresAt")
            cleaned_expires_at = expires_at.split(".")[0]
            self.token_expiry = datetime.fromisoformat(
                cleaned_expires_at
            ) - timedelta(minutes=5)
            logger_bot.info(f"Новый IAM-токен получен и "
                            f"истекает: {expires_at}")
        except requests.exceptions.RequestException as e:
            logger_bot.error("Ошибка при получении IAM-токена:", e)

    def get_token(self):
        if not self.iam_token or datetime.now() >= self.token_expiry:
            self.refresh_token()
        return self.iam_token
