import pycountry

COMMON_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "INR", "SAR",
    "AED", "TRY", "EGP", "JOD", "ILS", "KRW", "SEK", "NOK", "BRL", "MXN"
]

def get_common_currency_choices():
    choices = []
    for code in COMMON_CURRENCIES:
        currency = pycountry.currencies.get(alpha_3=code)
        if currency:
            choices.append((currency.alpha_3, f"{currency.alpha_3} - {currency.name}"))
    return sorted(choices)