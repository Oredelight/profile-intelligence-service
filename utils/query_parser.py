import re

def parse_query(q: str):
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

    match = re.search(r"above (\d+)", q)
    if match:
        filters["min_age"] = int(match.group(1))

    countries = {
        "nigeria": "NG",
        "kenya": "KE",
        "angola": "AO"
    }

    for name, code in countries.items():
        if name in q:
            filters["country_id"] = code

    return filters if filters else None