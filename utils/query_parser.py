import re

COUNTRY_MAP = {
    "nigeria": "NG",
    "kenya": "KE",
    "angola": "AO",
    "benin": "BJ",
    "ghana": "GH",
    "south africa": "ZA",
    "egypt": "EG",
    "morocco": "MA",
    "uganda": "UG",
    "tanzania": "TZ",
    "sudan": "SD",
    "ethiopia": "ET",
    "cameroon": "CM",
    "senegal": "SN",
    "mali": "ML",
    "dr congo": "CD",
    "democratic republic of congo": "CD",
    "congo": "CG",
    "ivory coast": "CI",
    "côte d'ivoire": "CI",
    "zambia": "ZM",
    "zimbabwe": "ZW",
    "mozambique": "MZ",
    "madagascar": "MG",
    "rwanda": "RW",
    "somalia": "SO",
    "south sudan": "SS",
    "namibia": "NA",
    "botswana": "BW",
    "malawi": "MW",
    "burkina faso": "BF",
    "niger": "NE",
    "guinea": "GN",
    "togo": "TG",
    "sierra leone": "SL",
    "liberia": "LR",
    "united states": "US",
    "usa": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "france": "FR",
    "germany": "DE",
    "india": "IN",
    "brazil": "BR",
    "australia": "AU",
    "canada": "CA",
    "china": "CN",
    "japan": "JP",
}

AGE_GROUP_MAP = {
    "child": "child",
    "children": "child",
    "teen": "teenager",
    "teenager": "teenager",
    "teenagers": "teenager",
    "adolescent": "teenager",
    "adult": "adult",
    "adults": "adult",
    "senior": "senior",
    "seniors": "senior",
    "elderly": "senior",
    "old": "senior",
}


def parse_query(q: str):
    if not q:
        return None

    q_lower = q.lower().strip()
    filters = {}

    has_male = re.search(r'\bmales?\b', q_lower) is not None
    has_female = re.search(r'\bfemales?\b', q_lower) is not None

    if has_male and not has_female:
        filters["gender"] = "male"
    elif has_female and not has_male:
        filters["gender"] = "female"

    # Parse age groups
    for term, age_group in AGE_GROUP_MAP.items():
        if term in q_lower:
            filters["age_group"] = age_group
            break

    if "young" in q_lower:
        filters["min_age"] = 16
        filters["max_age"] = 24

    match = re.search(r"(?:above|over)\s+(\d+)", q_lower)
    if match:
        filters["min_age"] = int(match.group(1))

    match = re.search(r"(?:below|under)\s+(\d+)", q_lower)
    if match:
        filters["max_age"] = int(match.group(1))

    match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", q_lower)
    if match:
        filters["min_age"] = int(match.group(1))
        filters["max_age"] = int(match.group(2))

    for country_name, code in COUNTRY_MAP.items():
        if country_name in q_lower:
            filters["country_id"] = code
            break

    return filters if filters else None
