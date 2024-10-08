from config import (AI_API_KEY, AI_BALANCE_URL, AI_HEADERS, AI_MAX_TOKENS,
                    AI_MODEL, AI_ROLE, AI_URL_API)
from modules.ovay_ai import OvayniseAI

ai_assistant = OvayniseAI(
    AI_API_KEY,
    AI_URL_API,
    AI_BALANCE_URL,
    AI_MODEL,
    AI_ROLE,
    AI_MAX_TOKENS,
    AI_HEADERS,
)
