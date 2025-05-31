import requests
from decouple import config
from django.conf import settings

EXCHANGE_RATE_API_KEY = config('EXCHANGE_RATE_API_KEY')
BASE_URL = "https://v6.exchangerate-api.com/v6"
def fetch_exchange_rates(base_currency="JOD"):

    url = f"{BASE_URL}/{EXCHANGE_RATE_API_KEY}/latest/{base_currency}"
    response = requests.get(url)
    if response.status_code==200:
        data = response.json()
        return data.get('conversion_rates',{})
    else:
        raise Exception(f"Exchange API error:{response.status_code},{response.text}")
