"""Authoritative ISO 4217 Currency metadata repository and lookup utilities."""

from typing import Any

# Authoritative ISO 3166-1 alpha-2 -> ISO 4217 currency specification
COUNTRY_CURRENCY_REGISTRY: dict[str, dict[str, str]] = {
    "IN": {"code": "INR", "symbol": "₹", "name": "Indian Rupee"},
    "JP": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen"},
    "US": {"code": "USD", "symbol": "$", "name": "US Dollar"},
    "GB": {"code": "GBP", "symbol": "£", "name": "British Pound"},
    "FR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "DE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "IT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "ES": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "NL": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "BE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "AT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "PT": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "IE": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "FI": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "GR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "HR": {"code": "EUR", "symbol": "€", "name": "Euro"},
    "SG": {"code": "SGD", "symbol": "S$", "name": "Singapore Dollar"},
    "AE": {"code": "AED", "symbol": "د.إ", "name": "UAE Dirham"},
    "AU": {"code": "AUD", "symbol": "A$", "name": "Australian Dollar"},
    "CA": {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar"},
    "CH": {"code": "CHF", "symbol": "CHF", "name": "Swiss Franc"},
    "CN": {"code": "CNY", "symbol": "¥", "name": "Chinese Yuan"},
    "BR": {"code": "BRL", "symbol": "R$", "name": "Brazilian Real"},
    "ZA": {"code": "ZAR", "symbol": "R", "name": "South African Rand"},
    "RU": {"code": "RUB", "symbol": "₽", "name": "Russian Ruble"},
    "KR": {"code": "KRW", "symbol": "₩", "name": "South Korean Won"},
    "MX": {"code": "MXN", "symbol": "Mex$", "name": "Mexican Peso"},
    "ID": {"code": "IDR", "symbol": "Rp", "name": "Indonesian Rupiah"},
    "TR": {"code": "TRY", "symbol": "₺", "name": "Turkish Lira"},
    "SA": {"code": "SAR", "symbol": "﷼", "name": "Saudi Riyal"},
    "SE": {"code": "SEK", "symbol": "kr", "name": "Swedish Krona"},
    "NO": {"code": "NOK", "symbol": "kr", "name": "Norwegian Krone"},
    "DK": {"code": "DKK", "symbol": "kr", "name": "Danish Krone"},
    "NZ": {"code": "NZD", "symbol": "NZ$", "name": "New Zealand Dollar"},
    "TH": {"code": "THB", "symbol": "฿", "name": "Thai Baht"},
    "MY": {"code": "MYR", "symbol": "RM", "name": "Malaysian Ringgit"},
    "PH": {"code": "PHP", "symbol": "₱", "name": "Philippine Peso"},
    "PL": {"code": "PLN", "symbol": "zł", "name": "Polish Zloty"},
    "IL": {"code": "ILS", "symbol": "₪", "name": "Israeli Shekel"},
    "EG": {"code": "EGP", "symbol": "E£", "name": "Egyptian Pound"},
    "PK": {"code": "PKR", "symbol": "₨", "name": "Pakistani Rupee"},
    "BD": {"code": "BDT", "symbol": "৳", "name": "Bangladeshi Taka"},
    "LK": {"code": "LKR", "symbol": "Rs", "name": "Sri Lankan Rupee"},
    "NP": {"code": "NPR", "symbol": "रू", "name": "Nepalese Rupee"},
    "VN": {"code": "VND", "symbol": "₫", "name": "Vietnamese Dong"},
    "NG": {"code": "NGN", "symbol": "₦", "name": "Nigerian Naira"},
    "KE": {"code": "KES", "symbol": "KSh", "name": "Kenyan Shilling"},
    "AR": {"code": "ARS", "symbol": "$", "name": "Argentine Peso"},
    "CL": {"code": "CLP", "symbol": "$", "name": "Chilean Peso"},
    "CO": {"code": "COP", "symbol": "$", "name": "Colombian Peso"},
    "PE": {"code": "PEN", "symbol": "S/.", "name": "Peruvian Sol"},
    "CZ": {"code": "CZK", "symbol": "Kč", "name": "Czech Koruna"},
    "HU": {"code": "HUF", "symbol": "Ft", "name": "Hungarian Forint"},
    "RO": {"code": "RON", "symbol": "lei", "name": "Romanian Leu"},
    "BG": {"code": "BGN", "symbol": "лв", "name": "Bulgarian Lev"},
    "UA": {"code": "UAH", "symbol": "₴", "name": "Ukrainian Hryvnia"},
    "AF": {"code": "AFN", "symbol": "؋", "name": "Afghan Afghani"},
    "AO": {"code": "AOA", "symbol": "Kz", "name": "Angolan Kwanza"},
    "HK": {"code": "HKD", "symbol": "HK$", "name": "Hong Kong Dollar"},
    "TW": {"code": "TWD", "symbol": "NT$", "name": "New Taiwan Dollar"},
}

DEFAULT_CURRENCY: dict[str, str] = {
    "code": "USD",
    "symbol": "$",
    "name": "US Dollar",
}


def get_currency_for_country(iso2: str | None) -> dict[str, str]:
    """Retrieve ISO 4217 currency metadata for a given country ISO-2 code."""
    if not iso2:
        return dict(DEFAULT_CURRENCY)
    clean_iso = iso2.strip().upper()
    return dict(COUNTRY_CURRENCY_REGISTRY.get(clean_iso, DEFAULT_CURRENCY))


def get_currency_symbol(currency_code: str | None) -> str:
    """Return recognized symbol for currency code or code itself."""
    if not currency_code:
        return "$"
    clean_code = currency_code.strip().upper()
    for item in COUNTRY_CURRENCY_REGISTRY.values():
        if item["code"] == clean_code:
            return item["symbol"]
    return clean_code


def get_supported_currencies() -> list[dict[str, str]]:
    """Return unique list of all currencies supported across countries."""
    seen: set[str] = set()
    currencies: list[dict[str, str]] = []
    for item in COUNTRY_CURRENCY_REGISTRY.values():
        code = item["code"]
        if code not in seen:
            seen.add(code)
            currencies.append(dict(item))
    currencies.sort(key=lambda x: x["code"])
    return currencies

