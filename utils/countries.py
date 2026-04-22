COUNTRY_MAP = {
    "NG": "Nigeria",
    "KE": "Kenya",
    "AO": "Angola",
    "US": "United States",
    "GB": "United Kingdom",
}

def get_country_name(code: str):
    return COUNTRY_MAP.get(code, code)