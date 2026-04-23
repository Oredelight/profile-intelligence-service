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
}


def parse_query(q: str):
    if not q:
        return None

    q = q.lower().strip()

    filters = {}

    has_male = "male" in q
    has_female = "female" in q

    if has_male and not has_female:
        filters["gender"] = "male"
    elif has_female and not has_male:
        filters["gender"] = "female"
   
    if "child" in q:
        filters["age_group"] = "child"
    elif "teen" in q:
        filters["age_group"] = "teenager"
    elif "adult" in q:
        filters["age_group"] = "adult"
    elif "senior" in q:
        filters["age_group"] = "senior"


    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24

    match = re.search(r"above\s+(\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    # below X → max_age
    match = re.search(r"below\s+(\d+)", q)
    if match:
        filters["max_age"] = int(match.group(1))

    # between X and Y → both
    match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))
        filters["max_age"] = int(match.group(2))

    for country_name, code in COUNTRY_MAP.items():
        if country_name in q:
            filters["country_id"] = code
            break

    return filters if filters else None