from config import crypto_headers, crypto_parameters, crypto_url
from modules.api.crypto import Crypto

crypto_shower = Crypto(crypto_url, crypto_headers, crypto_parameters)
